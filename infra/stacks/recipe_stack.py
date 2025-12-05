from aws_cdk import (
    Stack,
    Duration,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_s3 as s3,
    aws_lambda as lambda_,
    aws_events as events,
    aws_events_targets as targets,
    aws_secretsmanager as secretsmanager,
    aws_iam as iam,
    RemovalPolicy,
    CfnOutput,
)
from constructs import Construct
from utils import Config


class RecipeStack(Stack):
    """
    레시피 추천 서비스 스택

    Dependencies:
    - BackendStack (VPC, 공유 RDS, 공유 S3 버킷, Secrets)

    Resources:
    - Lambda Function (Recipe Sync from 식품안전나라 API)
    - EventBridge Rule (매주 월요일 오전 02시)
    - Security Groups

    Database:
    - BackendStack의 공유 RDS 인스턴스 사용
    - Database: fridger
    - Tables: recipe, recipe_recommendations

    S3 Storage:
    - 레시피 썸네일 이미지: s3://bucket/recipes/{recipe_id}/thumbnail.jpg
    - 레시피 조리 과정 이미지: s3://bucket/recipes/{recipe_id}/manual_01.jpg ~ manual_20.jpg
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.IVpc,
        db_instance: rds.IDatabaseInstance,
        lambda_sg: ec2.ISecurityGroup,
        uploads_bucket: s3.IBucket,
        food_safety_api_secret: secretsmanager.ISecret,
        recipe_sync_metadata_secret: secretsmanager.ISecret,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 파라미터 저장
        self.vpc = vpc
        self.db_instance = db_instance
        self.lambda_sg = lambda_sg
        self.uploads_bucket = uploads_bucket
        self.food_safety_api_secret = food_safety_api_secret
        self.recipe_sync_metadata_secret = recipe_sync_metadata_secret

        is_production = Config.get("Production", False)
        removal_policy = (
            RemovalPolicy.RETAIN if is_production else RemovalPolicy.DESTROY
        )


        # ======================
        # Lambda Function - Recipe Sync
        # ======================

        database_name = "fridger"  # 공유 데이터베이스
        database_username = "fridger"  # 공유 사용자

        # Config에서 Recipe 설정 가져오기
        recipe_config = Config.get("Recipe", {})
        lambda_timeout_minutes = recipe_config.get("timeout_minutes", 15)
        lambda_memory_size = recipe_config.get("memory_size", 1024)

        # Lambda 함수 생성
        #
        # NOTE: 프로덕션 배포 시에는 bundling을 활성화해야 합니다!
        # Docker Desktop 설치 후 주석 해제
        #
        import os
        skip_bundling = os.environ.get("CDK_SKIP_BUNDLING", "false").lower() == "true"

        self.recipe_sync_lambda = lambda_.Function(
            self,
            "RecipeSyncLambda",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="recipe_sync_handler.lambda_handler",
            code=lambda_.Code.from_asset(
                ".",  # 전체 프로젝트 디렉토리 마운트
                exclude=[
                    "cdk.out",
                    ".git",
                    ".gitignore",
                    "*.md",
                    "**/__pycache__",
                    "venv",
                    ".venv",
                    ".env",
                    "tests",
                    "infra",
                ],
                bundling=None if skip_bundling else {
                    "image": lambda_.Runtime.PYTHON_3_12.bundling_image,
                    "command": [
                        "bash", "-c",
                        # Lambda 패키지 구조:
                        # /asset-output/
                        #   ├── recipe_sync_handler.py (handler)
                        #   ├── requirements.txt
                        #   ├── app/ (FastAPI 애플리케이션 디렉토리)
                        #   │   ├── core/
                        #   │   ├── models/
                        #   │   ├── services/
                        #   │   └── utils/
                        #   └── [installed dependencies from requirements.txt]
                        "pip install -r lambda/requirements.txt -t /asset-output && "
                        "cp -r lambda/* /asset-output/ && "
                        "cp -r app /asset-output/app"
                    ],
                }
            ),
            timeout=Duration.minutes(lambda_timeout_minutes),
            memory_size=lambda_memory_size,
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS  # NAT Gateway 통한 인터넷 접근
            ),
            security_groups=[self.lambda_sg],
            environment={
                "ENVIRONMENT": "production",
                "SERVICE_NAME": "recipe",
                "DATABASE_HOST": self.db_instance.db_instance_endpoint_address,
                "DATABASE_PORT": "5432",
                "DATABASE_NAME": database_name,
                "DATABASE_USER": database_username,
                "DB_SECRET_NAME": self.db_instance.secret.secret_name if self.db_instance.secret else "",
                "FOOD_SAFETY_API_SECRET_NAME": self.food_safety_api_secret.secret_name,
                "RECIPE_SYNC_METADATA_SECRET_NAME": self.recipe_sync_metadata_secret.secret_name,
                # AWS_REGION은 Lambda 런타임에서 자동으로 설정됨 (예약된 환경 변수)
                "FOOD_SAFETY_API_BASE_URL": "http://openapi.foodsafetykorea.go.kr/api",
                "S3_BUCKET_NAME": self.uploads_bucket.bucket_name,
                "S3_RECIPE_PREFIX": "recipes",
            },
        )

        # Lambda에 권한 부여
        if self.db_instance.secret:
            self.db_instance.secret.grant_read(self.recipe_sync_lambda)
        self.food_safety_api_secret.grant_read(self.recipe_sync_lambda)
        self.recipe_sync_metadata_secret.grant_read(self.recipe_sync_lambda)
        self.recipe_sync_metadata_secret.grant_write(self.recipe_sync_lambda)

        # S3 버킷 쓰기 권한 부여 (ACL 설정 포함)
        self.uploads_bucket.grant_write(self.recipe_sync_lambda)
        self.uploads_bucket.grant_read(self.recipe_sync_lambda)

        # 명시적으로 PutObjectAcl 권한 추가
        self.recipe_sync_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=["s3:PutObjectAcl"],
                resources=[f"{self.uploads_bucket.bucket_arn}/*"]
            )
        )

        # ======================
        # EventBridge Rule - 매주 월요일 오전 02시 KST
        # ======================

        # 매월 1일 04:00 KST = 전월 마지막 날 19:00 UTC (전날)
        # 예: 5월 1일 04:00 KST -> 4월 30일 19:00 UTC
        self.recipe_sync_rule = events.Rule(
            self,
            "RecipeSyncRule",
            description="Trigger Recipe Sync Lambda every 1st day of month at 04:00 AM KST",
            schedule=events.Schedule.cron(
                minute="0",
                hour="19",  # UTC 19:00
                day="L",    # L = Last day of the month (월의 마지막 날)
            ),
        )

        # Lambda를 타겟으로 추가
        self.recipe_sync_rule.add_target(
            targets.LambdaFunction(self.recipe_sync_lambda)
        )


        # Outputs
        CfnOutput(
            self,
            "RecipeSyncLambdaArn",
            value=self.recipe_sync_lambda.function_arn,
            description="Recipe Sync Lambda Function ARN",
        )

        CfnOutput(
            self,
            "RecipeSyncSchedule",
            value="Every Monday at 02:00 AM KST (Sunday 17:00 UTC)",
            description="Recipe Sync EventBridge Schedule",
        )
