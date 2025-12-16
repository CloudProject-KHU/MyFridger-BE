from __future__ import annotations

from aws_cdk import (
    DefaultStackSynthesizer,
    Duration,
    RemovalPolicy,
    Stack,
    SecretValue,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_s3 as s3,
    aws_s3_assets as s3_assets,
    aws_secretsmanager as secretsmanager,
    aws_lambda as lambda_,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
    CfnOutput,
)
from constructs import Construct

from utils import Config


class BackendStack(Stack):
    """
    백엔드와 DB를 셋업합니다.
    - RDS: Postgres 16.3
    - EC2: Amazon Linux 2023에서 FastAPI 백엔드 서비스 실행
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        synthesizer = DefaultStackSynthesizer(generate_bootstrap_version_rule=False)

        super().__init__(scope, construct_id, synthesizer=synthesizer, **kwargs)

        is_production = Config.get("Production", False)
        removal_policy = (
            RemovalPolicy.RETAIN if is_production else RemovalPolicy.DESTROY
        )

        # ==============================================
        # Secret Manager
        # ==============================================
        # Food Safety API Key를 Secret Manager에 저장
        self.food_safety_api_secret = secretsmanager.Secret(
            self,
            "FoodSafetyAPISecret",
            secret_name="fridger/food-safety-api-key",
            description="Food Safety Korea API Key",
            secret_string_value=SecretValue.unsafe_plain_text(
                '{"api_key": "YOUR_API_KEY_HERE"}'  # 배포 후 콘솔에서 변경
            )
        )
        self.ocr_api_key = secretsmanager.Secret(
            self,
            "OcrAPISecret",
            secret_name="fridger/ocr-api-key",
            description="OCR API Key",
            secret_string_value=SecretValue.unsafe_plain_text(
                'OCR_KEY_HERE'  # 배포 후 콘솔에서 변경
            )
        )
        self.cognito_user_pool_url = secretsmanager.Secret(
            self,
            "CognitoUserPoolUrl",
            secret_name="fridger/cognito-user-pool-url",
            description="Cognito User Pool URL",
            secret_string_value=SecretValue.unsafe_plain_text(
                'COGNITO_USER_POOL_URL_HERE'  # 배포 후 콘솔에서 변경
            )
        )

        # Recipe Sync Metadata를 Secret Manager에 저장
        # 초기값은 20000101로 설정
        initial_date = "20000101"
        self.recipe_sync_metadata_secret = secretsmanager.Secret(
            self,
            "RecipeSyncMetadataSecret",
            secret_name="fridger/recipe-sync-metadata",
            description="Recipe sync metadata including last sync date",
            secret_string_value=SecretValue.unsafe_plain_text(
                f'{{"last_sync_date": "{initial_date}"}}'
            )
        )

        # ==============================================
        # VPC
        # ==============================================
        # VPC 설정
        self.vpc = ec2.Vpc(
            self,
            "BackendVpc",
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
            max_azs=2,
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public", subnet_type=ec2.SubnetType.PUBLIC, cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,  # NAT Gateway 사용 (Lambda, S3 용)
                    cidr_mask=24,
                ),
                ec2.SubnetConfiguration(
                    name="Isolated",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,  # RDS 용
                    cidr_mask=24,
                )
            ],
        )
        # VPC Endpoint 추가 (Lambda -> S3 접근 (인터넷 말고 곧바로 S3로 전달))
        self.vpc.add_gateway_endpoint(
            "S3Endpoint",
            service=ec2.GatewayVpcEndpointAwsService.S3,
            subnets=[ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)]
        )

        # ==============================================
        # Session Manager
        # ==============================================
        # Session Manager를 위한 VPC Interface Endpoints 추가 (프리티어)
        # Public Subnet에 배치하여 EC2 인스턴스가 접근 가능하도록 설정
        self.vpc.add_interface_endpoint(
           "SSMEndpoint",
           service=ec2.InterfaceVpcEndpointAwsService.SSM,
           subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
        )
        self.vpc.add_interface_endpoint(
            "SSMMessagesEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.SSM_MESSAGES,
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
        )
        self.vpc.add_interface_endpoint(
            "EC2MessagesEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.EC2_MESSAGES,
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
        )

        # ==============================================
        # Security Group
        # ==============================================
        # EC2 보안 그룹
        ec2_sg = ec2.SecurityGroup(
            self,
            "EC2SecurityGroup",
            vpc=self.vpc,
            description="allow SSH, HTTP, HTTPS",
            allow_all_outbound=True,
        )
        ec2_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "allow SSH")
        ec2_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "allow HTTP")
        ec2_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(443), "allow HTTPS")

        # RDS 보안 그룹
        self.db_sg = ec2.SecurityGroup(
            self,
            "DBSecurityGroup",
            vpc=self.vpc,
            description="allow EC2 only",
            allow_all_outbound=False,
        )
        self.db_sg.add_ingress_rule(ec2_sg, ec2.Port.tcp(5432), "allow EC2")

        # Lambda 보안 그룹
        self.lambda_sg = ec2.SecurityGroup(
            self,
            "LambdaSecurityGroup",
            vpc=self.vpc,
            description="Security group for Lambda functions",
            allow_all_outbound=True,
        )
        self.db_sg.add_ingress_rule(
            peer=self.lambda_sg,
            connection=ec2.Port.tcp(5432),
            description="Allow connection from Recipe Lambda"
        )


        # ==============================================
        # RDS, EC2 Instance
        # ==============================================
        # DB 인스턴스 (RDS)
        database_name = "fridger"
        database_username = "fridger"
        credentials = rds.Credentials.from_generated_secret(
            username=database_username,
            exclude_characters='"@/\\"\'',
        )
        self.db_instance = rds.DatabaseInstance(
            self,
            "BackendDBInstance",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_16
            ),
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3,
                ec2.InstanceSize.MICRO,
            ),
            security_groups=[self.db_sg],
            database_name=database_name,
            credentials=credentials,
            backup_retention=Duration.days(0),
            allocated_storage=20,
            storage_type=rds.StorageType.GP3,
            max_allocated_storage=20,
            multi_az=False,
            publicly_accessible=False,
            removal_policy=removal_policy,
            deletion_protection=False,
        )

        # EC2 인스턴스
        app_asset = s3_assets.Asset(
            self,
            "FastAPIAsset",
            path="./",
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
                "lambda",
            ],
        )
        key_pair = ec2.CfnKeyPair(
            self,
            "FridgerKeyPair",
            key_name="fridger-backend",
        )
        self.ec2_instance = ec2.Instance(
            self,
            "BackendInstance",
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T3, ec2.InstanceSize.MICRO
            ),
            machine_image=ec2.MachineImage.latest_amazon_linux2023(),
            security_group=ec2_sg,
            key_name=key_pair.key_name,
        )

        if self.db_instance.secret is None:
            raise ValueError("DB instance secret is None")

        app_asset.grant_read(self.ec2_instance.role)
        self.db_instance.secret.grant_read(self.ec2_instance.role)

        # Bedrock 권한 추가 (AI 기반 소비기한 추정)
        self.ec2_instance.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonBedrockFullAccess")
        )

        environment_variables = {
            "ENVIRONMENT": "production",
            "DATABASE_HOST": self.db_instance.db_instance_endpoint_address,
            "DATABASE_PORT": "5432",
            "DATABASE_NAME": database_name,
            "DATABASE_USER": database_username,
            "DATABASE_PASSWORD": (
                credentials.password if credentials.password is not None else ""
            ),
            "DB_SECRET_NAME": self.db_instance.secret.secret_name,
            "OCR_SECRET_NAME": self.ocr_api_key.secret_name,
            "AWS_REGION": self.region,
        }
        env_content = "\n".join([f"{k}={v}" for k, v in environment_variables.items()])
        commands = ec2.UserData.for_linux()
        commands.add_commands(
            # 필수 패키지 설치
            "dnf update -y",
            "dnf install -y python3-pip unzip",
            "curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR='/usr/local/bin' sh",  # uv 설치

            # 애플리케이션 코드 다운로드 및 압축 해제
            "mkdir -p ~/app",
            f"aws s3 cp {app_asset.s3_object_url} ~/app/app.zip",
            "unzip ~/app/app.zip -d ~/app",

            f"cat <<EOF > ~/app/.env\n{env_content}\nEOF",  # .env 생성
            # Secrets Manager에서 비밀번호 파싱 후 .env에 추가
            f"export DB_SECRET_NAME={self.db_instance.secret.secret_name}",
            f"export AWS_REGION={self.region}",
            f"export OCR_SECRET_NAME={self.ocr_api_key.secret_name}",
            f"export COGNITO_SECRET_NAME={self.cognito_user_pool_url.secret_name}",

            # DB secret inject
            "DB_SECRET_JSON=$(aws secretsmanager get-secret-value --secret-id $DB_SECRET_NAME --region $AWS_REGION --query SecretString --output text)",
            "DB_PASSWORD=$(echo $DB_SECRET_JSON | jq -r .password)",
            'echo "DATABASE_PASSWORD=$DB_PASSWORD" >> ~/app/.env',
            # OCR API Key inject
            "OCR_API_KEY=$(aws secretsmanager get-secret-value --secret-id $OCR_SECRET_NAME --region $AWS_REGION --query SecretString --output text)",
            'echo "OCR_API_KEY=$OCR_API_KEY" >> ~/app/.env',
            # Cognito User Pool URL inject
            "COGNITO_USER_POOL_URL=$(aws secretsmanager get-secret-value --secret-id $COGNITO_SECRET_NAME --region $AWS_REGION --query SecretString --output text)",
            'echo "AWS_COGNITO_USER_POOL=$COGNITO_USER_POOL_URL" >> ~/app/.env',

            # 의존성 설치 및 실행
            "cd ~/app && uv sync",
            "cd ~/app && uv run alembic upgrade head",
            "cd ~/app && nohup uv run uvicorn app.main:app --host 0.0.0.0 --port 80 --app-dir ~/app &",
        )
        self.ec2_instance.add_user_data(commands.render())


        # ==============================================
        #  EIP attach
        # ==============================================
        # 새로운 EIP 생성하여 EC2에 연결하는 방식
        # self.eip = ec2.CfnEIP(
        #     self,
        #     "BackendEIP",
        #     instance_id=self.ec2_instance.instance_id
        # )

        # Config에서 기존 EIP 정보 가져오기
        materials_config = Config.get("Materials", {})
        existing_eip_allocation_id = materials_config.get("eip_allocation_id")
        existing_eip_address = materials_config.get("eip_address")

        if not existing_eip_allocation_id or not existing_eip_address:
            raise ValueError(
                "Materials EIP configuration is missing. "
                "Please set 'Materials.eip_allocation_id' and 'Materials.eip_address' in infra/utils.py"
            )

        # 기존 EIP를 새 EC2 인스턴스에 연결
        self.eip_association = ec2.CfnEIPAssociation(
            self,
            "MaterialsEIPAssociation",
            allocation_id=existing_eip_allocation_id,
            instance_id=self.ec2_instance.instance_id,
        )

        # ==============================================
        #  S3 Instance
        # ==============================================
        # S3 버킷 - 이미지 업로드
        self.uploads_bucket = s3.Bucket(
            self,
            "UploadsBucket",
            bucket_name=f"myfridger-uploads-{self.account}-{self.region}",
            removal_policy=removal_policy,
            auto_delete_objects=not is_production,
            versioned=is_production,
            encryption=s3.BucketEncryption.S3_MANAGED,
            # Public Read 접근 허용 (레시피 이미지를 인터넷 사용자가 볼 수 있도록)
            public_read_access=True,
            object_ownership=s3.ObjectOwnership.OBJECT_WRITER,  # ACL 사용 허용
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False
            ),
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
        self.uploads_bucket.grant_read(self.ec2_instance.role)


        CfnOutput(
            self,
            "VpcId",
            value=self.vpc.vpc_id,
            export_name="BackendVpc",
        )
