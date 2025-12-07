"""
Recipe Manual Sync Lambda Handler

관리자가 AWS CLI 또는 AWS 콘솔에서 수동으로 호출하는 Lambda 함수입니다.
특정 범위의 레시피만 동기화합니다.

호출 방법 (AWS CLI):
    aws lambda invoke \
        --function-name MyFridger-Recipe-ManualRecipeSync \
        --payload '{"start_index": 1, "end_index": 100}' \
        response.json

호출 방법 (AWS Console):
    Lambda 콘솔 > Test 탭 > Event JSON:
    {
        "start_index": 1,
        "end_index": 100
    }
"""
import sys
import os
import asyncio
import json
from datetime import datetime

# Lambda 환경에서 app 모듈을 import하기 위한 경로 설정
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


async def sync_recipes_by_range_async(start_index: int, end_index: int):
    """
    비동기로 특정 범위의 레시피 동기화 실행
    """
    from app.core.db import async_engine
    from sqlmodel.ext.asyncio.session import AsyncSession
    from app.services.recipe_sync_service import recipe_sync_service

    async with AsyncSession(async_engine) as session:
        total_synced = await recipe_sync_service.sync_recipes_by_range(
            session=session,
            start_index=start_index,
            end_index=end_index
        )
        return total_synced


def lambda_handler(event, context):
    """
    Lambda 핸들러 함수 (수동 호출용)

    Args:
        event: 입력 이벤트 객체
            {
                "start_index": 1,      # 필수: 시작 인덱스
                "end_index": 100       # 필수: 끝 인덱스
            }
        context: Lambda 실행 컨텍스트

    Returns:
        statusCode: 200 (성공) 또는 400/500 (실패)
        body: 동기화 결과 메시지
    """
    try:
        print(f"Manual recipe sync started at {datetime.utcnow()}")
        print(f"Event: {json.dumps(event)}")

        # 1. 입력 파라미터 검증
        start_index = event.get('start_index')
        end_index = event.get('end_index')

        if start_index is None or end_index is None:
            error_msg = "Missing required parameters: start_index and end_index"
            print(f"Error: {error_msg}")
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': error_msg,
                    'usage': {
                        'start_index': 'Required, integer >= 1',
                        'end_index': 'Required, integer >= start_index'
                    },
                    'example': {
                        'start_index': 1,
                        'end_index': 100
                    }
                })
            }

        # 타입 변환 및 검증
        try:
            start_index = int(start_index)
            end_index = int(end_index)
        except (ValueError, TypeError):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'start_index and end_index must be integers'
                })
            }

        if start_index < 1 or end_index < start_index:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Invalid range: start_index must be >= 1 and end_index >= start_index',
                    'received': {
                        'start_index': start_index,
                        'end_index': end_index
                    }
                })
            }

        print(f"Syncing recipes from {start_index} to {end_index}...")

        # 2. DB 비밀번호 설정
        if not settings.DATABASE_PASSWORD:
            print("Fetching DB password from Secrets Manager...")
            db_password = get_db_password()
            if db_password:
                settings.DATABASE_PASSWORD = db_password
                print("DB password successfully set.")
            else:
                raise ValueError("Failed to retrieve DB password.")

        # 3. 비동기 함수 실행
        total_synced = asyncio.run(sync_recipes_by_range_async(start_index, end_index))

        message = f"Manual recipe sync completed. Synced {total_synced} recipes from index {start_index} to {end_index}"
        print(message)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': message,
                'range': {
                    'start_index': start_index,
                    'end_index': end_index
                },
                'total_synced': total_synced,
                'timestamp': datetime.utcnow().isoformat()
            })
        }

    except Exception as e:
        error_message = f"Manual recipe sync failed: {str(e)}"
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
        "start_index": 1,
        "end_index": 10
    }

    test_context = {}

    result = lambda_handler(test_event, test_context)
    print("\n=== Test Result ===")
    print(json.dumps(result, indent=2))
