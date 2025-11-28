"""
Materials Stack - 식재료 관리 서비스

Materials API 서버:
- EC2 인스턴스 (FastAPI Materials Service)
- Security Groups
- Elastic IP
- CommonStack의 공유 RDS 사용
"""
from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_s3_assets as s3_assets,
)
from constructs import Construct
from utils import Config


class MaterialsStack(Stack):
    """
    식재료 관리 서비스 스택

    Dependencies:
    - CommonStack (VPC, 공유 RDS)

    Resources:
    - EC2 Instance (Materials API)
    - Security Groups
    - Elastic IP

    Database:
    - CommonStack의 공유 RDS 인스턴스 사용
    - Database: myfridger_db
    - Tables: materials
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.IVpc,
        db_instance: rds.IDatabaseInstance,
        db_security_group: ec2.ISecurityGroup,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        is_production = Config.get("Production", False)
        removal_policy = (
            RemovalPolicy.RETAIN if is_production else RemovalPolicy.DESTROY
        )

        # ======================
        # Security Groups
        # ======================

        # EC2 보안 그룹
        self.ec2_sg = ec2.SecurityGroup(
            self,
            "MaterialsEC2SG",
            vpc=vpc,
            description="Security group for Materials API EC2",
            allow_all_outbound=True,
        )
        self.ec2_sg.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(22),
            "Allow SSH"
        )
        self.ec2_sg.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(80),
            "Allow HTTP"
        )
        self.ec2_sg.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(443),
            "Allow HTTPS"
        )

        # 공유 RDS 보안 그룹에 EC2 접근 허용
        db_security_group.add_ingress_rule(
            self.ec2_sg,
            ec2.Port.tcp(5432),
            "Allow Materials EC2 to access Shared DB"
        )

        # ======================
        # EC2 Instance - Materials API
        # ======================

        # 애플리케이션 코드 에셋
        app_asset = s3_assets.Asset(
            self,
            "MaterialsAPIAsset",
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

        # Key Pair
        key_pair = ec2.CfnKeyPair(
            self,
            "MaterialsKeyPair",
            key_name="myfridger-materials",
        )

        # EC2 인스턴스
        self.ec2_instance = ec2.Instance(
            self,
            "MaterialsAPIInstance",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T3,
                ec2.InstanceSize.MICRO
            ),
            machine_image=ec2.MachineImage.latest_amazon_linux2023(),
            security_group=self.ec2_sg,
            key_name=key_pair.key_name,
        )

        # 권한 부여
        if db_instance.secret is None:
            raise ValueError("DB instance secret is None")

        app_asset.grant_read(self.ec2_instance.role)
        db_instance.secret.grant_read(self.ec2_instance.role)

        # 환경 변수 설정
        database_name = "myfridger_db"  # 공유 데이터베이스
        database_username = "myfridger_admin"  # 공유 사용자

        environment_variables = {
            "ENVIRONMENT": "production",
            "SERVICE_NAME": "materials",
            "DATABASE_HOST": db_instance.db_instance_endpoint_address,
            "DATABASE_PORT": "5432",
            "DATABASE_NAME": database_name,
            "DATABASE_USER": database_username,
            "DB_SECRET_NAME": db_instance.secret.secret_name,
            "AWS_REGION": self.region,
        }

        env_content = "\n".join([f"{k}={v}" for k, v in environment_variables.items()])

        # User Data 스크립트
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
            # 시스템 업데이트 및 필수 패키지 설치
            "dnf update -y",
            "dnf install -y python3-pip unzip jq",

            # uv 설치
            "curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR='/usr/local/bin' sh",

            # 애플리케이션 디렉토리 생성
            "mkdir -p /opt/materials-api",

            # S3에서 애플리케이션 코드 다운로드
            f"aws s3 cp {app_asset.s3_object_url} /opt/materials-api/app.zip",

            # 압축 해제
            "unzip /opt/materials-api/app.zip -d /opt/materials-api",

            # .env 파일 생성
            f"cat <<EOF > /opt/materials-api/.env\n{env_content}\nEOF",

            # Secrets Manager에서 DB 비밀번호 가져오기
            f"export DB_SECRET_NAME={db_instance.secret.secret_name}",
            f"export AWS_REGION={self.region}",
            "SECRET_JSON=$(aws secretsmanager get-secret-value --secret-id $DB_SECRET_NAME --region $AWS_REGION --query SecretString --output text)",
            "DB_PASSWORD=$(echo $SECRET_JSON | jq -r .password)",
            'echo "DATABASE_PASSWORD=$DB_PASSWORD" >> /opt/materials-api/.env',

            # 의존성 설치
            "cd /opt/materials-api && uv sync",

            # 데이터베이스 마이그레이션 실행
            "cd /opt/materials-api && uv run alembic upgrade head",

            # FastAPI 서버 실행 (백그라운드)
            "cd /opt/materials-api && nohup uv run uvicorn app.main:app --host 0.0.0.0 --port 80 > /var/log/materials-api.log 2>&1 &",
        )

        self.ec2_instance.add_user_data(user_data.render())

        # ======================
        # Elastic IP
        # ======================
        self.eip = ec2.CfnEIP(
            self,
            "MaterialsEIP",
            instance_id=self.ec2_instance.instance_id,
        )

        # ======================
        # Outputs
        # ======================
        from aws_cdk import CfnOutput

        CfnOutput(
            self,
            "MaterialsAPIPublicIP",
            value=self.eip.attr_public_ip,
            description="Materials API Public IP (Elastic IP)",
        )

        CfnOutput(
            self,
            "MaterialsAPIURL",
            value=f"http://{self.eip.attr_public_ip}",
            description="Materials API Base URL",
        )
