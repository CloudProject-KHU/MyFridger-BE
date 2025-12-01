"""
Recipe Sync Lambda Handler

EventBridge에 의해 매주 월요일 오전 02시에 실행됩니다.
외부 식품안전나라 API에서 레시피 데이터를 가져와 RDS에 저장합니다.
"""
import sys
import os
import asyncio
import json
from datetime import datetime

# Lambda 환경에서 app 모듈을 import하기 위한 경로 설정
# CDK bundling으로 app 디렉토리가 Lambda 패키지 루트에 위치함
sys.path.insert(0, os.path.dirname(__file__))

from app.core.config import settings


def get_db_password():
    """
    AWS Secrets Manager에서 DB 비밀번호를 가져옵니다.
    """
    import boto3
    
    secret_name = os.environ.get("DB_SECRET_NAME")
    region_name = os.environ.get("AWS_REGION", "ap-northeast-2")

    if not secret_name:
        print("Warning: DB_SECRET_NAME environment variable is not set.")
        return None

    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    try:
        response = client.get_secret_value(SecretId=secret_name)
        if 'SecretString' in response:
            secret = response['SecretString']
            return json.loads(secret).get('password')
    except Exception as e:
        print(f"Error fetching secret: {e}")
        raise e
    return None


async def sync_recipes_async():
    """
    비동기로 레시피 동기화 실행
    """
    from app.core.db import async_engine
    from sqlmodel.ext.asyncio.session import AsyncSession
    from app.services.recipe_sync_service import recipe_sync_service

    async with AsyncSession(async_engine) as session:
        total_synced = await recipe_sync_service.sync_all_recipes(
            session=session,
            batch_size=500,
            use_incremental=True  # 마지막 동기화 이후 변경된 레시피만 가져옴
        )
        return total_synced


def lambda_handler(event, context):
    """
    Lambda 핸들러 함수

    Args:
        event: EventBridge에서 전달되는 이벤트 객체
        context: Lambda 실행 컨텍스트

    Returns:
        statusCode: 200 (성공) 또는 500 (실패)
        body: 동기화 결과 메시지
    """
    try:
        print(f"Recipe sync started at {datetime.utcnow()}")
        print(f"Event: {json.dumps(event)}")

        # 1. DB 비밀번호가 설정되어 있지 않다면 Secrets Manager에서 가져옵니다.
        if not settings.DATABASE_PASSWORD:
            print("Fetching DB password from Secrets Manager...")
            db_password = get_db_password()
            if db_password:
                settings.DATABASE_PASSWORD = db_password
                print("DB password successfully set.")
            else:
                raise ValueError("Failed to retrieve DB password.")

        # 비동기 함수 실행
        total_synced = asyncio.run(sync_recipes_async())

        message = f"Recipe sync completed successfully. Total synced: {total_synced} recipes"
        print(message)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': message,
                'total_synced': total_synced,
                'timestamp': datetime.utcnow().isoformat()
            })
        }

    except Exception as e:
        error_message = f"Recipe sync failed: {str(e)}"
        print(error_message)
        print(f"Error type: {type(e).__name__}")

        import traceback
        traceback.print_exc()

        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': error_message,
                'timestamp': datetime.utcnow().isoformat()
            })
        }


# 로컬 테스트용
if __name__ == "__main__":
    # 테스트 이벤트
    test_event = {
        "version": "0",
        "id": "test-event-id",
        "detail-type": "Scheduled Event",
        "source": "aws.events",
        "time": datetime.utcnow().isoformat()
    }

    test_context = {}

    result = lambda_handler(test_event, test_context)
    print("\n=== Test Result ===")
    print(json.dumps(result, indent=2))
