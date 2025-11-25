import re
from typing import Optional
import httpx
import boto3
from botocore.exceptions import ClientError

from core.config import settings


class S3Helper:
    def __init__(self):
        self.s3_client = boto3.client('s3', region_name=settings.AWS_REGION)
        self.bucket_name = settings.S3_BUCKET_NAME

    async def upload_image_from_url(
        self, 
        image_url: str, 
        recipe_id: int, 
        image_index: int
    ) -> Optional[str]:
        """
        이미지 URL에서 다운로드하여 S3에 업로드
        
        Args:
            image_url: 원본 이미지 URL
            recipe_id: 레시피 ID
            image_index: 이미지 순서
            
        Returns:
            S3 URL 또는 None (실패 시)
        """
        if not image_url or image_url == '':
            return None
        
        try:
            # 이미지 다운로드
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(image_url)
                response.raise_for_status()
                image_data = response.content
            
            # 파일 확장자 추출
            extension = image_url.split('.')[-1].lower()
            if extension not in ['jpg', 'jpeg', 'png', 'gif']:
                extension = 'jpg'
            
            # S3 키 생성 (recipe_instruction_images/{recipe_id}/{index}.{ext})
            s3_key = f"recipe_instruction_images/{recipe_id}/{image_index}.{extension}"
            
            # Content-Type 설정
            content_type_map = {
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'gif': 'image/gif'
            }
            content_type = content_type_map.get(extension, 'image/jpeg')
            
            # S3에 업로드
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=image_data,
                ContentType=content_type,
                CacheControl='max-age=31536000'  # 1년 캐싱
            )
            
            # S3 URL 반환
            s3_url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"
            return s3_url
            
        except Exception as e:
            print(f"Failed to upload image {image_url}: {str(e)}")
            return None

    def delete_recipe_images(self, recipe_id: int):
        """레시피의 모든 이미지 삭제"""
        try:
            prefix = f"recipes/{recipe_id}/"
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' in response:
                objects = [{'Key': obj['Key']} for obj in response['Contents']]
                self.s3_client.delete_objects(
                    Bucket=self.bucket_name,
                    Delete={'Objects': objects}
                )
        except ClientError as e:
            print(f"Failed to delete images for recipe {recipe_id}: {str(e)}")


s3_helper = S3Helper()