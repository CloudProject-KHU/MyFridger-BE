from __future__ import annotations

from aws_cdk import (
    DefaultStackSynthesizer,
    Duration,
    RemovalPolicy,
    Stack,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_s3_assets as s3_assets,
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

        # VPC 설정
        vpc = ec2.Vpc(
            self,
            "BackendVpc",
            max_azs=2,
            nat_gateways=0,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public", subnet_type=ec2.SubnetType.PUBLIC, cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Isolated",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24,
                ),
            ],
        )

        # EC2 보안 그룹
        ec2_sg = ec2.SecurityGroup(
            self,
            "EC2SecurityGroup",
            vpc=vpc,
            description="allow SSH, HTTP, HTTPS",
            allow_all_outbound=True,
        )
        ec2_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "allow SSH")
        ec2_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "allow HTTP")
        ec2_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(443), "allow HTTPS")

        # RDS 보안 그룹
        db_sg = ec2.SecurityGroup(
            self,
            "DBSecurityGroup",
            vpc=vpc,
            description="allow EC2 only",
            allow_all_outbound=False,
        )
        db_sg.add_ingress_rule(ec2_sg, ec2.Port.tcp(5432), "allow EC2")

        # DB 인스턴스
        database_name = "fridger"
        database_username = "fridger"
        credentials = rds.Credentials.from_generated_secret(
            username=database_username,
            exclude_characters='"@/\\',
        )
        db_instance = rds.DatabaseInstance(
            self,
            "BackendDBInstance",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_16
            ),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3,
                ec2.InstanceSize.MICRO,
            ),
            security_groups=[db_sg],
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
            ],
        )
        key_pair = ec2.CfnKeyPair(
            self,
            "FridgerKeyPair",
            key_name="fridger-backend",
        )
        ec2_instance = ec2.Instance(
            self,
            "BackendInstance",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T3, ec2.InstanceSize.MICRO
            ),
            machine_image=ec2.MachineImage.latest_amazon_linux2023(),
            security_group=ec2_sg,
            key_name=key_pair.key_name,
        )
        app_asset.grant_read(ec2_instance.role)

        environment_variables = {
            "DATABASE_HOST": db_instance.db_instance_endpoint_address,
            "DATABASE_PORT": "5432",
            "DATABASE_NAME": database_name,
            "DATABASE_USER": database_username,
            "DATABASE_PASSWORD": (
                credentials.password if credentials.password is not None else ""
            ),
        }
        env_content = "\n".join([f"{k}={v}" for k, v in environment_variables.items()])
        commands = ec2.UserData.for_linux()
        commands.add_commands(
            # 필수 패키지 설치
            "dnf update -y",
            "dnf install -y python3-pip unzip",
            "curl -LsSf https://astral.sh/uv/install.sh | sh",  # uv 설치
            # 애플리케이션 코드 다운로드
            "mkdir -p ~/app",
            f"aws s3 cp {app_asset.s3_object_url} ~/app/app.zip",
            # 어플리케이션 압축 해제
            "unzip ~/app/app.zip -d ~/app",
            f"cat <<EOF > ~/app/.env\n{env_content}\nEOF",  # .env 생성
            # 의존성 설치 및 실행
            "uv sync",
            "nohup uv run uvicorn main:app --host 0.0.0.0 --port 80 --app-dir ~/app",
        )
        ec2_instance.add_user_data(commands.render())
