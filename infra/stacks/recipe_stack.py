"""
Recipe Stack - 레시피 추천 서비스

Recipe Sync Lambda:
- Lambda Function (Recipe Sync)
- EventBridge (매주 월요일 오전 02시 KST)
- Security Groups
- S3 (레시피 이미지 저장)
- CommonStack의 공유 RDS 사용
"""
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
)
from constructs import Construct
from utils import Config


class RecipeStack(Stack):
    """
    레시피 추천 서비스 스택

    Dependencies:
    - CommonStack (VPC, 공유 RDS, Secrets)

    Resources:
    - Lambda Function (Recipe Sync from 식품안전나라 API)
    - EventBridge Rule (매주 월요일 오전 02시)
    - Security Groups

    Database:
    - CommonStack의 공유 RDS 인스턴스 사용
    - Database: myfridger_db
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
        db_security_group: ec2.ISecurityGroup,
        uploads_bucket: s3.IBucket,
        food_safety_api_secret: secretsmanager.ISecret,
        recipe_sync_metadata_secret: secretsmanager.ISecret,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ======================
        # Security Groups
        # ======================

        # Lambda 보안 그룹
        self.lambda_sg = ec2.SecurityGroup(
            self,
            "RecipeLambdaSG",
            vpc=vpc,
            description="Security group for Recipe Sync Lambda",
            allow_all_outbound=True,
        )

        # 공유 RDS 보안 그룹에 Lambda 접근 허용
        db_security_group.add_ingress_rule(
            self.lambda_sg,
            ec2.Port.tcp(5432),
            "Allow Recipe Lambda to access Shared DB"
        )

        # ======================
        # Lambda Function - Recipe Sync
        # ======================

        database_name = "myfridger_db"  # 공유 데이터베이스
        database_username = "myfridger_admin"  # 공유 사용자

        # Lambda 함수 생성
        self.recipe_sync_lambda = lambda_.Function(
            self,
            "RecipeSyncLambda",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="recipe_sync_handler.lambda_handler",
            code=lambda_.Code.from_asset(
                "./lambda",
                bundling={
                    "image": lambda_.Runtime.PYTHON_3_12.bundling_image,
                    "command": [
                        "bash", "-c",
                        "pip install -r requirements.txt -t /asset-output && "
                        "cp -r . /asset-output && "
                        "cp -r ../app /asset-output/"  # app 디렉토리도 포함
                    ],
                }
            ),
            timeout=Duration.minutes(15),  # 레시피 동기화는 시간이 걸릴 수 있음
            memory_size=1024,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            security_groups=[self.lambda_sg],
            environment={
                "ENVIRONMENT": "production",
                "SERVICE_NAME": "recipe",
                "DATABASE_HOST": db_instance.db_instance_endpoint_address,
                "DATABASE_PORT": "5432",
                "DATABASE_NAME": database_name,
                "DATABASE_USER": database_username,
                "DB_SECRET_NAME": db_instance.secret.secret_name if db_instance.secret else "",
                "AWS_REGION": self.region,
                "FOOD_SAFETY_API_BASE_URL": "http://openapi.foodsafetykorea.go.kr/api",
                "S3_BUCKET_NAME": uploads_bucket.bucket_name,
                "S3_RECIPE_PREFIX": "recipes",
            },
        )

        # Lambda에 권한 부여
        if db_instance.secret:
            db_instance.secret.grant_read(self.recipe_sync_lambda)
        food_safety_api_secret.grant_read(self.recipe_sync_lambda)
        recipe_sync_metadata_secret.grant_read(self.recipe_sync_lambda)
        recipe_sync_metadata_secret.grant_write(self.recipe_sync_lambda)

        # S3 버킷 쓰기 권한 부여
        uploads_bucket.grant_put(self.recipe_sync_lambda)
        uploads_bucket.grant_read(self.recipe_sync_lambda)

        # ======================
        # EventBridge Rule - 매주 월요일 오전 02시 KST
        # ======================

        # KST 02:00 = UTC 17:00 (전날)
        # 매주 월요일 02:00 KST = 일요일 17:00 UTC
        self.recipe_sync_rule = events.Rule(
            self,
            "RecipeSyncRule",
            description="Trigger Recipe Sync Lambda every Monday at 02:00 AM KST",
            schedule=events.Schedule.cron(
                minute="0",
                hour="17",  # UTC 17:00
                week_day="SUN",  # 일요일 (다음날 월요일 02:00 KST)
            ),
        )

        # Lambda를 타겟으로 추가
        self.recipe_sync_rule.add_target(
            targets.LambdaFunction(self.recipe_sync_lambda)
        )

        # ======================
        # Outputs
        # ======================
        from aws_cdk import CfnOutput

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
