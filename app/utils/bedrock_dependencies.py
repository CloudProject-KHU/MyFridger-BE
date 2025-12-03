import boto3
from functools import lru_cache

from app.core.config import settings
from app.services.expiry_estimation_service import ExpiryEstimationService

# 1. Bedrock 클라이언트 생성 함수 (Resource가 무거우므로 캐싱 권장)
@lru_cache()
def get_bedrock_client():
    """
    Bedrock 클라이언트를 한 번만 생성하고 재사용 (Singleton 패턴 효과)
    """
    return boto3.client(
        'bedrock-runtime',
        region_name=settings.BEDROCK_REGION  # Amazon Bedrock (Nova Lite) 지원 리전 사용
    )

# 2. Service 생성 함수 (Singleton 패턴)
# @lru_cache를 붙이면 전역 변수처럼 '싱글톤'으로 동작합니다 (객체를 한 번만 생성)
@lru_cache()
def get_expiry_service() -> ExpiryEstimationService:
    """
    ExpiryEstimationService를 한 번만 생성하고 재사용
    """
    client = get_bedrock_client()
    return ExpiryEstimationService(bedrock_client=client)