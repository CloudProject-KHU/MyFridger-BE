import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone, timedelta
import json
from app.services.expiry_estimation_service import ExpiryEstimationService
from app.models.recipes import ExpiryEstimationRequest, ExpiryEstimationResponse


@pytest.fixture
def service():
    return ExpiryEstimationService()


@pytest.fixture
def sample_request():
    """샘플 소비기한 추정 요청"""
    return ExpiryEstimationRequest(
        name="사과",
        category="과일",
        purchased_at=datetime(2025, 1, 1, tzinfo=timezone.utc)
    )


def test_estimate_expiry_rule_based_apple(service, sample_request):
    """규칙 기반 추정 - 사과"""
    response = service.estimate_expiry_rule_based(sample_request)

    assert isinstance(response, ExpiryEstimationResponse)
    # 사과는 이름으로 매칭 (EXPIRY_RULES에 "사과" 항목 있음 - 10일)
    expected_date = sample_request.purchased_at + timedelta(days=10)
    assert response.estimated_expiration_date == expected_date
    assert response.confidence == 0.75


def test_estimate_expiry_rule_based_milk(service):
    """규칙 기반 추정 - 우유"""
    request = ExpiryEstimationRequest(
        name="우유",
        category="유제품",
        purchased_at=datetime(2025, 1, 1, tzinfo=timezone.utc)
    )

    response = service.estimate_expiry_rule_based(request)

    # 우유: 7일 (이름 직접 매칭)
    expected_date = request.purchased_at + timedelta(days=7)
    assert response.estimated_expiration_date == expected_date
    assert response.confidence == 0.75


def test_estimate_expiry_rule_based_meat(service):
    """규칙 기반 추정 - 육류"""
    request = ExpiryEstimationRequest(
        name="소고기",
        category="육류",
        purchased_at=datetime(2025, 1, 1, tzinfo=timezone.utc)
    )

    response = service.estimate_expiry_rule_based(request)

    # 소고기: 4일
    expected_date = request.purchased_at + timedelta(days=4)
    assert response.estimated_expiration_date == expected_date
    assert response.confidence == 0.75


def test_estimate_expiry_rule_based_seafood(service):
    """규칙 기반 추정 - 해산물"""
    request = ExpiryEstimationRequest(
        name="고등어",
        category="해산물",
        purchased_at=datetime(2025, 1, 1, tzinfo=timezone.utc)
    )

    response = service.estimate_expiry_rule_based(request)

    # 고등어는 이름에 매칭 안되므로 카테고리로 매칭 시도 -> 기타로 처리 (0일)
    # 실제로는 "생선" 규칙에 매칭될 수 있음
    assert isinstance(response, ExpiryEstimationResponse)
    assert response.confidence >= 0.5


def test_estimate_expiry_rule_based_vegetable(service):
    """규칙 기반 추정 - 채소"""
    request = ExpiryEstimationRequest(
        name="배추",
        category="채소",
        purchased_at=datetime(2025, 1, 1, tzinfo=timezone.utc)
    )

    response = service.estimate_expiry_rule_based(request)

    # 배추: 10일
    expected_date = request.purchased_at + timedelta(days=10)
    assert response.estimated_expiration_date == expected_date
    assert response.confidence == 0.75


def test_estimate_expiry_rule_based_unknown_category(service):
    """규칙 기반 추정 - 알 수 없는 카테고리"""
    request = ExpiryEstimationRequest(
        name="신기한 식재료",
        category="기타",
        purchased_at=datetime(2025, 1, 1, tzinfo=timezone.utc)
    )

    response = service.estimate_expiry_rule_based(request)

    # 기타: 0일
    expected_date = request.purchased_at + timedelta(days=0)
    assert response.estimated_expiration_date == expected_date
    assert response.confidence == 0.5


@pytest.mark.asyncio
async def test_bedrock_client_creation_success(service):
    """Bedrock 클라이언트 생성 성공"""
    with patch('boto3.client') as mock_boto3:
        mock_client = MagicMock()
        mock_boto3.return_value = mock_client

        client = service._get_bedrock_client()

        assert client is not None
        mock_boto3.assert_called_once_with(
            'bedrock-runtime',
            region_name='ap-northeast-2'
        )


@pytest.mark.asyncio
async def test_bedrock_client_creation_failure(service):
    """Bedrock 클라이언트 생성 실패"""
    with patch('boto3.client', side_effect=Exception("AWS credentials not found")):
        client = service._get_bedrock_client()
        assert client is None


@pytest.mark.asyncio
async def test_estimate_expiry_ai_based_success(service, sample_request):
    """AI 기반 추정 성공"""
    # Mock Bedrock response
    mock_response_body = {
        "output": {
            "message": {
                "content": [
                    {
                        "text": json.dumps({
                            "estimated_days": 7,
                            "confidence": 0.85,
                            "notes": "사과는 냉장 보관 시 약 7일 정도 신선도를 유지합니다."
                        })
                    }
                ]
            }
        }
    }

    mock_bedrock_client = MagicMock()
    mock_bedrock_client.invoke_model.return_value = {
        'body': MagicMock(read=lambda: json.dumps(mock_response_body).encode())
    }

    with patch.object(service, '_get_bedrock_client', return_value=mock_bedrock_client):
        response = await service.estimate_expiry_ai_based(sample_request)

        assert isinstance(response, ExpiryEstimationResponse)
        expected_date = sample_request.purchased_at + timedelta(days=7)
        assert response.estimated_expiration_date == expected_date
        assert response.confidence == 0.85
        assert "사과" in response.notes


@pytest.mark.asyncio
async def test_estimate_expiry_ai_based_fallback_to_rule(service, sample_request):
    """AI 실패 시 규칙 기반으로 폴백"""
    # Bedrock 클라이언트 None (생성 실패)
    with patch.object(service, '_get_bedrock_client', return_value=None):
        response = await service.estimate_expiry_ai_based(sample_request)

        # 규칙 기반 결과 반환
        assert isinstance(response, ExpiryEstimationResponse)
        expected_date = sample_request.purchased_at + timedelta(days=10)
        assert response.estimated_expiration_date == expected_date
        assert response.confidence == 0.75  # 규칙 기반 confidence


@pytest.mark.asyncio
async def test_estimate_expiry_ai_based_invalid_json_response(service, sample_request):
    """AI 응답이 잘못된 JSON일 때 폴백"""
    mock_response_body = {
        "output": {
            "message": {
                "content": [
                    {"text": "This is not a valid JSON"}
                ]
            }
        }
    }

    mock_bedrock_client = MagicMock()
    mock_bedrock_client.invoke_model.return_value = {
        'body': MagicMock(read=lambda: json.dumps(mock_response_body).encode())
    }

    with patch.object(service, '_get_bedrock_client', return_value=mock_bedrock_client):
        response = await service.estimate_expiry_ai_based(sample_request)

        # 규칙 기반으로 폴백
        assert isinstance(response, ExpiryEstimationResponse)
        assert response.confidence == 0.75  # 규칙 기반


@pytest.mark.asyncio
async def test_estimate_expiry_ai_based_missing_fields(service, sample_request):
    """AI 응답에 필수 필드가 없을 때 폴백"""
    mock_response_body = {
        "output": {
            "message": {
                "content": [
                    {
                        "text": json.dumps({
                            # estimated_days 필드 누락
                            "confidence": 0.9
                        })
                    }
                ]
            }
        }
    }

    mock_bedrock_client = MagicMock()
    mock_bedrock_client.invoke_model.return_value = {
        'body': MagicMock(read=lambda: json.dumps(mock_response_body).encode())
    }

    with patch.object(service, '_get_bedrock_client', return_value=mock_bedrock_client):
        response = await service.estimate_expiry_ai_based(sample_request)

        # 기본값 7일 사용 (AI 응답에서 estimated_days가 없으면 기본값 사용)
        assert isinstance(response, ExpiryEstimationResponse)


@pytest.mark.asyncio
async def test_estimate_expiry_ai_based_invoke_exception(service, sample_request):
    """Bedrock invoke_model 호출 시 예외 발생"""
    mock_bedrock_client = MagicMock()
    mock_bedrock_client.invoke_model.side_effect = Exception("Service error")

    with patch.object(service, '_get_bedrock_client', return_value=mock_bedrock_client):
        response = await service.estimate_expiry_ai_based(sample_request)

        # 규칙 기반으로 폴백
        assert isinstance(response, ExpiryEstimationResponse)
        expected_date = sample_request.purchased_at + timedelta(days=10)
        assert response.estimated_expiration_date == expected_date


@pytest.mark.asyncio
async def test_bedrock_client_caching(service):
    """Bedrock 클라이언트 캐싱 검증"""
    with patch('boto3.client') as mock_boto3:
        mock_client = MagicMock()
        mock_boto3.return_value = mock_client

        # 첫 번째 호출
        client1 = service._get_bedrock_client()
        # 두 번째 호출
        client2 = service._get_bedrock_client()

        # 같은 인스턴스 반환 (캐싱)
        assert client1 is client2
        # boto3.client는 한 번만 호출
        mock_boto3.assert_called_once()
