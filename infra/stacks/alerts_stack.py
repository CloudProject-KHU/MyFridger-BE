"""
Alerts Stack - 유통기한 알림 서비스 (구조 및 설명)

Alert Checker Lambda:
- Lambda Function (Alert Checker - 유통기한 임박 식재료 체크)
- EventBridge (매일 오전 9시 KST)
- SNS Topics (웹 푸시, 이메일, SMS)
- SQS Queues (비동기 알림 처리)
- CommonStack의 공유 RDS 사용

주요 기능:
1. 매일 오전 9시에 Lambda가 실행되어 모든 사용자의 식재료 유통기한 체크
2. D-7, D-3, D-1, D-Day에 해당하는 식재료 필터링
3. 사용자 알림 설정(alert_preferences)에 따라 알림 발송
4. SNS를 통해 웹 푸시/이메일/SMS 발송
5. alerts 테이블에 발송 이력 저장 (clicked_at으로 KPI 측정)
"""
from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_lambda as lambda_,
    aws_events as events,
    aws_events_targets as targets,
    aws_sns as sns,
    aws_sqs as sqs,
)
from constructs import Construct
from utils import Config


class AlertsStack(Stack):
    """
    유통기한 알림 서비스 스택

    Dependencies:
    - CommonStack (VPC, 공유 RDS)

    Resources:
    - Lambda Function (Alert Checker)
    - EventBridge Rule (매일 오전 9시 KST = 매일 0시 UTC)
    - SNS Topics (웹 푸시, 이메일, SMS)
    - SQS Queues (비동기 알림 처리용)
    - Security Groups

    Database:
    - CommonStack의 공유 RDS 인스턴스 사용
    - Database: myfridger_db
    - Tables: alert_preferences, alerts, materials (조회용)

    테이블 스키마:
    - alert_preferences: 사용자별 알림 설정
      - user_id, enabled, alert_time, channels (push/email/sms)
      - d7_enabled, d3_enabled, d1_enabled, d0_enabled
    - alerts: 알림 발송 이력
      - user_id, material_id, alert_type, sent_at, clicked_at, channel, status

    Lambda 환경 변수:
    - DATABASE_HOST: 공유 RDS 엔드포인트
    - DATABASE_NAME: myfridger_db
    - SNS_PUSH_TOPIC_ARN: 웹 푸시 SNS Topic
    - SNS_EMAIL_TOPIC_ARN: 이메일 SNS Topic
    - SNS_SMS_TOPIC_ARN: SMS SNS Topic

    EventBridge Schedule:
    - cron(0 0 * * ? *) = 매일 0시 UTC = 매일 9시 KST
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

        # TODO: 구현 필요
        # 1. Lambda 보안 그룹 생성
        # 2. 공유 RDS 보안 그룹에 Lambda 접근 허용
        # 3. SNS Topics 생성 (웹 푸시, 이메일, SMS)
        # 4. SQS Queues 생성 (각 채널별)
        # 5. Lambda 함수 생성 (Alert Checker)
        #    - 공유 DB에서 materials, alert_preferences 조회
        #    - 알림 메시지 생성 및 SQS에 전송
        # 6. EventBridge Rule 생성 (매일 0시 UTC)
        # 7. Lambda에 권한 부여 (RDS, SNS, SQS, Secrets Manager)
        # 8. Outputs 설정

        pass


# Lambda Handler 예시 구조:
"""
lambda/alert_checker_handler.py

async def lambda_handler(event, context):
    # Step 1: Materials DB에서 유통기한 임박 식재료 조회
    expiring_materials = await get_expiring_materials()  # D-7, D-3, D-1, D-Day

    # Step 2: 사용자별로 그룹화
    user_materials_map = group_by_user(expiring_materials)

    # Step 3: 각 사용자의 알림 설정 확인
    for user_id, materials in user_materials_map.items():
        preferences = await get_user_alert_preferences(user_id)

        if not preferences.enabled:
            continue

        # Step 4: 알림 레벨별로 필터링
        for material in materials:
            days_left = (material.expired_at - now()).days
            alert_type = get_alert_type(days_left)  # D7, D3, D1, D0

            if not preferences[f"{alert_type.lower()}_enabled"]:
                continue

            # Step 5: 알림 메시지 생성
            message = generate_alert_message(material, alert_type)

            # Step 6: 알림 이력 저장
            alert_record = await save_alert(user_id, material.id, alert_type)

            # Step 7: SQS에 알림 전송
            for channel in preferences.channels:
                await send_to_queue(channel, user_id, message)

    return {"statusCode": 200, "message": "Alerts processed"}
"""
