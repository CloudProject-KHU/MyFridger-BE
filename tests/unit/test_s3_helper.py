import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from botocore.exceptions import ClientError
from app.utils.s3_helper import S3Helper


@pytest.fixture
def s3_helper():
    """S3Helper 인스턴스"""
    with patch('boto3.client'):
        helper = S3Helper()
        helper.bucket_name = "test-bucket"
        helper.s3_client = MagicMock()
        return helper


@pytest.mark.asyncio
async def test_upload_thumbnail_from_url_success(s3_helper):
    """썸네일 업로드 성공"""
    image_url = "https://example.com/image.jpg"
    recipe_id = 123

    # Mock httpx response
    mock_response = MagicMock()
    mock_response.content = b"fake_image_data"
    mock_response.raise_for_status = MagicMock()

    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

        result = await s3_helper.upload_thumbnail_from_url(image_url, recipe_id)

        # S3 URL 반환 확인
        assert result is not None
        assert "test-bucket" in result
        assert f"recipes/{recipe_id}/thumbnail.jpg" in result

        # S3 put_object 호출 확인
        s3_helper.s3_client.put_object.assert_called_once()
        call_args = s3_helper.s3_client.put_object.call_args
        assert call_args[1]['Bucket'] == "test-bucket"
        assert call_args[1]['Key'] == f"recipes/{recipe_id}/thumbnail.jpg"
        assert call_args[1]['ContentType'] == 'image/jpeg'


@pytest.mark.asyncio
async def test_upload_thumbnail_from_url_png(s3_helper):
    """PNG 썸네일 업로드"""
    image_url = "https://example.com/image.png"
    recipe_id = 456

    mock_response = MagicMock()
    mock_response.content = b"fake_png_data"
    mock_response.raise_for_status = MagicMock()

    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

        result = await s3_helper.upload_thumbnail_from_url(image_url, recipe_id)

        assert result is not None
        assert "thumbnail.png" in result

        call_args = s3_helper.s3_client.put_object.call_args
        assert call_args[1]['ContentType'] == 'image/png'


@pytest.mark.asyncio
async def test_upload_thumbnail_from_url_empty_url(s3_helper):
    """빈 URL일 때 None 반환"""
    result = await s3_helper.upload_thumbnail_from_url("", 123)
    assert result is None


@pytest.mark.asyncio
async def test_upload_thumbnail_from_url_http_error(s3_helper):
    """HTTP 요청 실패 시 None 반환"""
    image_url = "https://example.com/notfound.jpg"
    recipe_id = 789

    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=Exception("404 Not Found")
        )

        result = await s3_helper.upload_thumbnail_from_url(image_url, recipe_id)

        assert result is None


@pytest.mark.asyncio
async def test_upload_thumbnail_from_url_s3_error(s3_helper):
    """S3 업로드 실패 시 None 반환"""
    image_url = "https://example.com/image.jpg"
    recipe_id = 999

    mock_response = MagicMock()
    mock_response.content = b"fake_image_data"
    mock_response.raise_for_status = MagicMock()

    # S3 put_object 실패
    s3_helper.s3_client.put_object.side_effect = ClientError(
        {'Error': {'Code': 'AccessDenied'}}, 'PutObject'
    )

    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

        result = await s3_helper.upload_thumbnail_from_url(image_url, recipe_id)

        assert result is None


@pytest.mark.asyncio
async def test_upload_image_from_url_success(s3_helper):
    """조리 과정 이미지 업로드 성공"""
    image_url = "https://example.com/step1.jpg"
    recipe_id = 123
    image_index = 1

    mock_response = MagicMock()
    mock_response.content = b"fake_step_image"
    mock_response.raise_for_status = MagicMock()

    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

        result = await s3_helper.upload_image_from_url(image_url, recipe_id, image_index)

        assert result is not None
        assert f"recipes/{recipe_id}/manual_01.jpg" in result

        call_args = s3_helper.s3_client.put_object.call_args
        assert call_args[1]['Key'] == f"recipes/{recipe_id}/manual_01.jpg"


@pytest.mark.asyncio
async def test_upload_image_from_url_index_20(s3_helper):
    """조리 과정 이미지 20번째 업로드"""
    image_url = "https://example.com/step20.jpg"
    recipe_id = 123
    image_index = 20

    mock_response = MagicMock()
    mock_response.content = b"fake_step_image"
    mock_response.raise_for_status = MagicMock()

    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

        result = await s3_helper.upload_image_from_url(image_url, recipe_id, image_index)

        assert result is not None
        assert f"recipes/{recipe_id}/manual_20.jpg" in result


@pytest.mark.asyncio
async def test_upload_image_from_url_empty(s3_helper):
    """빈 URL일 때 None 반환"""
    result = await s3_helper.upload_image_from_url("", 123, 1)
    assert result is None


@pytest.mark.asyncio
async def test_upload_image_from_url_unknown_extension(s3_helper):
    """알 수 없는 확장자 => jpg로 기본 설정"""
    image_url = "https://example.com/step.unknown"
    recipe_id = 123
    image_index = 5

    mock_response = MagicMock()
    mock_response.content = b"fake_image"
    mock_response.raise_for_status = MagicMock()

    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

        result = await s3_helper.upload_image_from_url(image_url, recipe_id, image_index)

        assert result is not None
        assert "manual_05.jpg" in result

        call_args = s3_helper.s3_client.put_object.call_args
        assert call_args[1]['ContentType'] == 'image/jpeg'


def test_delete_recipe_images_success(s3_helper):
    """레시피 이미지 삭제 성공"""
    recipe_id = 123

    # Mock list_objects_v2 response
    s3_helper.s3_client.list_objects_v2.return_value = {
        'Contents': [
            {'Key': f'recipes/{recipe_id}/thumbnail.jpg'},
            {'Key': f'recipes/{recipe_id}/manual_01.jpg'},
            {'Key': f'recipes/{recipe_id}/manual_02.jpg'},
        ]
    }

    s3_helper.delete_recipe_images(recipe_id)

    # list_objects_v2 호출 확인
    s3_helper.s3_client.list_objects_v2.assert_called_once_with(
        Bucket="test-bucket",
        Prefix=f"recipes/{recipe_id}/"
    )

    # delete_objects 호출 확인
    s3_helper.s3_client.delete_objects.assert_called_once()
    call_args = s3_helper.s3_client.delete_objects.call_args
    assert len(call_args[1]['Delete']['Objects']) == 3


def test_delete_recipe_images_no_contents(s3_helper):
    """삭제할 이미지가 없을 때"""
    recipe_id = 456

    s3_helper.s3_client.list_objects_v2.return_value = {}

    s3_helper.delete_recipe_images(recipe_id)

    # delete_objects가 호출되지 않음
    s3_helper.s3_client.delete_objects.assert_not_called()


def test_delete_recipe_images_client_error(s3_helper):
    """S3 삭제 중 에러 발생 시 예외 처리"""
    recipe_id = 789

    s3_helper.s3_client.list_objects_v2.side_effect = ClientError(
        {'Error': {'Code': 'AccessDenied'}}, 'ListObjectsV2'
    )

    # 예외가 발생하지 않고 정상 종료
    s3_helper.delete_recipe_images(recipe_id)


@pytest.mark.asyncio
async def test_upload_gif_image(s3_helper):
    """GIF 이미지 업로드"""
    image_url = "https://example.com/animation.gif"
    recipe_id = 555

    mock_response = MagicMock()
    mock_response.content = b"GIF89a..."
    mock_response.raise_for_status = MagicMock()

    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

        result = await s3_helper.upload_thumbnail_from_url(image_url, recipe_id)

        assert result is not None
        assert "thumbnail.gif" in result

        call_args = s3_helper.s3_client.put_object.call_args
        assert call_args[1]['ContentType'] == 'image/gif'


@pytest.mark.asyncio
async def test_cache_control_header(s3_helper):
    """Cache-Control 헤더 설정 확인"""
    image_url = "https://example.com/image.jpg"
    recipe_id = 123

    mock_response = MagicMock()
    mock_response.content = b"image_data"
    mock_response.raise_for_status = MagicMock()

    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

        await s3_helper.upload_thumbnail_from_url(image_url, recipe_id)

        call_args = s3_helper.s3_client.put_object.call_args
        assert call_args[1]['CacheControl'] == 'max-age=31536000'
