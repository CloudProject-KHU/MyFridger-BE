from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_rds as rds,
    aws_ec2 as ec2,
    aws_s3_notifications as s3_notify,
    aws_iam as iam,
    RemovalPolicy,
    Duration,
)
from constructs import Construct

from infra.utils import Config


class ReceiptAnalysisStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        removalPolicy = (
            RemovalPolicy.RETAIN
            if Config.get("Production", False)
            else RemovalPolicy.DESTROY
        )

        # RDS and Lambda용 VPC
        vpc = ec2.Vpc.from_lookup(self, "receipt-vpc", vpc_name="receipt-vpc")

        # 영수증 Lamdba 트리거용 bucket
        bucket = s3.Bucket(
            self,
            "ReceiptBucket",
            removal_policy=removalPolicy,
            auto_delete_objects=True,
        )

        # Security Groups
        rds_sg = ec2.SecurityGroup.from_lookup_by_name(self, "rds-sg", "rds-sg", vpc)
        receipt_sg = ec2.SecurityGroup(
            self, "receipt-sg", vpc=vpc, allow_all_outbound=True
        )

        # RDS - Lambda Security Group 설정
        rds_sg.add_ingress_rule(
            receipt_sg, ec2.Port.tcp(5432), "Allow Receipt Lambda access"
        )

        db_instance = rds.DatabaseInstance.from_database_instance_attributes(
            self,
            "fridger-db",
            instance_identifier="fridger-db",
            instance_endpoint_address="TODO",  # "fridger-db.cluster-custom.us-east-1.rds.amazonaws.com",
            port=5432,
            security_groups=[rds_sg],
        )

        analyzer_lambda = _lambda.Function(
            self,
            "ReceiptAnalyzer",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="receipt.handler",
            code=_lambda.Code.from_asset("../lambda"),
            vpc=vpc,
            security_groups=[lambda_sg],
            environment={
                "DB_HOST": db_instance.db_instance_endpoint_address,
            },
            timeout=Duration.seconds(30),
        )

        bucket.grant_read(analyzer_lambda)

        analyzer_lambda.add_to_role_policy(
            iam.PolicyStatement(actions=["rekognition:DetectText"], resources=["*"])
        )

        bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3_notify.LambdaDestination(analyzer_lambda),
            s3.NotificationKeyFilter(suffix=".jpg"),
        )
