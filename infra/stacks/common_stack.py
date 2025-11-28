"""
Common Stack - 공통 리소스 관리

모든 마이크로서비스가 공유하는 공통 인프라 리소스:
- VPC 및 네트워크 구성
- RDS PostgreSQL (단일 인스턴스, 다중 데이터베이스)
- S3 버킷 (이미지, 파일 저장)
- Secrets Manager (API Keys 등)
- CloudWatch Logs

# 아키텍처 구조

  CommonStack (공유 리소스)
  ├── VPC
  ├── RDS PostgreSQL (myfridger_db) ← 단일 인스턴스
  │   ├── materials 테이블
  │   ├── recipe, recipe_recommendations 테이블
  │   ├── alert_preferences, alerts 테이블 (예정)
  │   └── users, refresh_tokens 테이블 (예정)
  ├── S3 (uploads)
  └── Secrets Manager

  MaterialsStack
  └── EC2 (FastAPI) → 공유 RDS 접근

  RecipeStack
  └── Lambda (Recipe Sync) → 공유 RDS 접근

  AlertsStack (TODO)
  └── Lambda (Alert Checker) → 공유 RDS 접근

  UsersStack (TODO)
  └── Cognito + Auth API → 공유 RDS 접근
"""
from aws_cdk import (
    Stack,
    SecretValue,
    RemovalPolicy,
    Duration,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_s3 as s3,
    aws_secretsmanager as secretsmanager,
    aws_logs as logs,
)
from constructs import Construct
from utils import Config


class CommonStack(Stack):
    """
    공통 인프라 스택

    Exports:
    - vpc: VPC 객체
    - db_instance: 공유 RDS PostgreSQL 인스턴스
    - db_security_group: RDS 보안 그룹
    - uploads_bucket: S3 업로드 버킷
    - food_safety_api_secret: 식품안전나라 API Key Secret

    Database Structure:
    - 단일 RDS 인스턴스에 여러 데이터베이스 생성
    - materials_db: Materials 테이블
    - recipe_db: Recipe, RecipeRecommendation 테이블
    - alerts_db: AlertPreferences, Alerts 테이블
    - users_db: Users, RefreshTokens 테이블
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        is_production = Config.get("Production", False)
        removal_policy = (
            RemovalPolicy.RETAIN if is_production else RemovalPolicy.DESTROY
        )

        # ======================
        # VPC 생성
        # ======================
        self.vpc = ec2.Vpc(
            self,
            "MyFridgerVpc",
            max_azs=2,
            nat_gateways=0,  # 비용 절감을 위해 NAT Gateway 없음
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="PrivateIsolated",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24
                ),
            ],
        )

        # ======================
        # RDS Security Group
        # ======================
        self.db_security_group = ec2.SecurityGroup(
            self,
            "SharedDBSG",
            vpc=self.vpc,
            description="Security group for shared RDS instance",
            allow_all_outbound=False,
        )

        # ======================
        # RDS PostgreSQL - 공유 인스턴스
        # ======================
        database_name = "myfridger_db"  # 기본 데이터베이스
        database_username = "myfridger_admin"

        credentials = rds.Credentials.from_generated_secret(
            username=database_username,
            exclude_characters="\"@/\\\"'",
        )

        self.db_instance = rds.DatabaseInstance(
            self,
            "SharedDBInstance",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_16
            ),
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3,
                ec2.InstanceSize.SMALL,  # 여러 서비스 공유를 위해 SMALL 사용
            ),
            security_groups=[self.db_security_group],
            database_name=database_name,
            credentials=credentials,
            backup_retention=Duration.days(7 if is_production else 0),
            allocated_storage=50,  # 여러 서비스 데이터를 위해 50GB
            storage_type=rds.StorageType.GP3,
            max_allocated_storage=200 if is_production else 50,
            multi_az=is_production,
            publicly_accessible=False,
            removal_policy=removal_policy,
            deletion_protection=is_production,
        )

        # ======================
        # S3 버킷 - 이미지 업로드
        # ======================
        self.uploads_bucket = s3.Bucket(
            self,
            "UploadsBucket",
            bucket_name=f"myfridger-uploads-{self.account}-{self.region}",
            removal_policy=removal_policy,
            auto_delete_objects=not is_production,
            versioned=is_production,
            encryption=s3.BucketEncryption.S3_MANAGED,
            cors=[
                s3.CorsRule(
                    allowed_methods=[
                        s3.HttpMethods.GET,
                        s3.HttpMethods.PUT,
                        s3.HttpMethods.POST,
                    ],
                    allowed_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
                    allowed_headers=["*"],
                )
            ],
        )

        # ======================
        # Secrets Manager
        # ======================

        # 식품안전나라 API Key
        self.food_safety_api_secret = secretsmanager.Secret(
            self,
            "FoodSafetyAPISecret",
            secret_name="fridger/food-safety-api-key",
            description="Food Safety Korea API Key for Recipe Sync",
            secret_string_value=SecretValue.unsafe_plain_text(
                '{"api_key": "YOUR_API_KEY_HERE"}'  # 배포 후 AWS 콘솔에서 변경
            ),
        )

        # Recipe Sync 메타데이터 (마지막 동기화 날짜)
        self.recipe_sync_metadata_secret = secretsmanager.Secret(
            self,
            "RecipeSyncMetadataSecret",
            secret_name="fridger/recipe-sync-metadata",
            description="Recipe sync metadata including last sync date",
            secret_string_value=SecretValue.unsafe_plain_text(
                '{"last_sync_date": "20000101"}'  # 초기값
            ),
        )

        # ======================
        # CloudWatch Log Groups
        # ======================
        self.app_log_group = logs.LogGroup(
            self,
            "AppLogGroup",
            log_group_name="/myfridger/application",
            retention=logs.RetentionDays.ONE_WEEK if not is_production else logs.RetentionDays.ONE_MONTH,
            removal_policy=removal_policy,
        )

        self.lambda_log_group = logs.LogGroup(
            self,
            "LambdaLogGroup",
            log_group_name="/myfridger/lambda",
            retention=logs.RetentionDays.ONE_WEEK if not is_production else logs.RetentionDays.TWO_WEEKS,
            removal_policy=removal_policy,
        )

        # ======================
        # Outputs
        # ======================
        # 다른 스택에서 참조할 수 있도록 Export
        from aws_cdk import CfnOutput

        CfnOutput(
            self,
            "VpcId",
            value=self.vpc.vpc_id,
            export_name="MyFridger-VpcId",
        )

        CfnOutput(
            self,
            "UploadsBucketName",
            value=self.uploads_bucket.bucket_name,
            export_name="MyFridger-UploadsBucketName",
        )

        CfnOutput(
            self,
            "FoodSafetyAPISecretArn",
            value=self.food_safety_api_secret.secret_arn,
            export_name="MyFridger-FoodSafetyAPISecretArn",
        )

        CfnOutput(
            self,
            "SharedDBEndpoint",
            value=self.db_instance.db_instance_endpoint_address,
            description="Shared RDS Endpoint (all services)",
            export_name="MyFridger-SharedDBEndpoint",
        )

        CfnOutput(
            self,
            "SharedDBPort",
            value=str(self.db_instance.db_instance_endpoint_port),
            description="Shared RDS Port",
            export_name="MyFridger-SharedDBPort",
        )

        CfnOutput(
            self,
            "SharedDBName",
            value=database_name,
            description="Shared RDS Database Name",
            export_name="MyFridger-SharedDBName",
        )
