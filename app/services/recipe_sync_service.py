import re
from typing import List, Dict, Optional
from datetime import datetime
import httpx
import json
import boto3
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.models.recipes import Recipe
from app.utils.s3_helper import s3_helper


class RecipeSyncService:
    def __init__(self):
        self.base_url = settings.FOOD_SAFETY_API_BASE_URL
        self._api_key = None
        self._secrets_client = None
        self._last_sync_date = None

    def _get_secrets_client(self):
        """Secrets Manager 클라이언트 생성 (lazy loading)"""
        if self._secrets_client is None:
            self._secrets_client = boto3.client(
                'secretsmanager',
                region_name=settings.AWS_REGION
            )
        return self._secrets_client
    

    def _get_api_key(self) -> str:
        """
        Secret Manager에서 API 키 가져오기
        한 번 가져온 후 캐시에 저장
        """
        if self._api_key is not None:
            return self._api_key
        
        # 개발 환경에서는 환경 변수 사용
        if settings.ENVIRONMENT == "development" and settings.FOOD_SAFETY_API_KEY:
            self._api_key = settings.FOOD_SAFETY_API_KEY
            return self._api_key
        
        # 프로덕션에서는 Secret Manager에서 가져오기
        try:
            client = self._get_secrets_client()
            response = client.get_secret_value(
                SecretId='fridger/food-safety-api-key'
            )
            secret = json.loads(response['SecretString'])
            self._api_key = secret['api_key']
            return self._api_key
        except Exception as e:
            print(f"Failed to get API key from Secret Manager: {str(e)}")
            # fallback to environment variable
            self._api_key = settings.FOOD_SAFETY_API_KEY
            return self._api_key
    
    def _get_last_sync_date(self) -> Optional[str]:
        """
        마지막 동기화 날짜를 Secret Manager에서 가져오기
        형식: YYYYMMDD (예: 20170101)
        """
        try:
            client = self._get_secrets_client()
            response = client.get_secret_value(
                SecretId='fridger/recipe-sync-metadata'
            )
            metadata = json.loads(response['SecretString'])
            return metadata.get('last_sync_date')
        except Exception as e:
            print(f"Failed to get last sync date: {str(e)}")
            # 첫 동기화이거나 실패 시
            return "20000101"
    
    
    def _update_last_sync_date(self, sync_date: str):
        """
        마지막 동기화 날짜를 Secret Manager에 저장
        """
        try:
            client = self._get_secrets_client()
            client.put_secret_value(
                SecretId='fridger/recipe-sync-metadata',
                SecretString=json.dumps({
                    'last_sync_date': sync_date
                })
            )
        except client.exceptions.ResourceNotFoundException:
            # Secret이 없으면 생성
            client.create_secret(
                Name='fridger/recipe-sync-metadata',
                Description='Recipe sync metadata including last sync date',
                SecretString=json.dumps({
                    'last_sync_date': sync_date
                })
            )
        except Exception as e:
            print(f"Failed to update last sync date: {str(e)}")


    def _parse_materials(self, rcp_parts_dtls: str) -> List[str]:
        """
        재료 문자열을 파싱하여 재료 이름 리스트로 변환
        예: '새우두부계란찜\n연두부 75g(3/4모), 칵테일새우 20g(5마리)...'
        -> ['연두부', '칵테일새우', '달걀', ...]
        """
        if not rcp_parts_dtls:
            return []
        
        # 줄바꿈으로 분리
        lines = rcp_parts_dtls.split('\n')
        materials = []
        
        for line in lines:
            # 제목 라인이나 빈 라인 또는 양념장 라인 스킵
            if not line.strip() or '·' in line:
                continue
            
            # 쉼표로 분리
            items = line.split(', ')
            for item in items:
                materials.append(item)
        
        return materials
    
    def _extract_instructions(self, recipe_data: Dict) -> List[str]:
        """
        MANUAL01~MANUAL20에서 조리 순서 추출
        """
        instructions = []
        for i in range(1, 21):
            key = f"MANUAL{i:02d}" if i >= 10 else f"MANUAL0{i}"
            manual = recipe_data.get(key, '').strip()
            if manual:
                # 끝의 a, b, c 등 제거
                manual = re.sub(r'[a-z]$', '', manual).strip()
                instructions.append(manual)
        return instructions
    
    async def fetch_recipes_from_api(
            self,
            start: int = 1,
            end: int = 999,
            change_date: Optional[str] = None
        ) -> List[Dict]:
        """
        식품의약품안전처 API에서 레시피 데이터 가져오기
        
        Args:
            start: 시작 인덱스
            end: 끝 인덱스 (최대 999개씩 가능)
            change_date: 변경일자 (YYYYMMDD 형식, 예: 20251126)
                            이 날짜 이후 변경된 레시피만 가져옴
        """
        self._get_api_key()

        if change_date:
            url = f"{self.base_url}/{self._api_key}/COOKRCP01/json/{start}/{end}/CHNG_DT={change_date}"
        else:
            url = f"{self.base_url}/{self._api_key}/COOKRCP01/json/{start}/{end}"
        
        try:
            print(f"Requesting URL: {url}")  # 디버깅: URL 출력

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(url)

                # 디버깅: 응답 상태 코드와 내용 출력
                print(f"Response status: {response.status_code}")
                print(f"Response headers: {dict(response.headers)}")
                print(f"Response text (first 500 chars): {response.text[:500]}")

                response.raise_for_status()
                data = response.json()

                # API 응답 구조: {serviceId: {total_count: ..., row: [...]}}
                service_id = 'COOKRCP01'
                if service_id in data and 'row' in data[service_id]:
                    print(f"Successfully parsed {len(data[service_id]['row'])} recipes")
                    return data[service_id]['row']
                else:
                    print(f"Unexpected API response structure: {list(data.keys())}")
                return []
        except Exception as e:
            print(f"Failed to fetch recipes from API: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return []
    
    async def sync_recipe(self, session: AsyncSession, recipe_data: Dict) -> Optional[Recipe]:
        """
        단일 레시피를 DB에 동기화
        """
        try:
            recipe_id = int(recipe_data['RCP_SEQ'])
            name = recipe_data['RCP_NM']
            recipe_pat = recipe_data.get('RCP_PAT2', '')
            method = recipe_data.get('RCP_WAY2', '')
            
            # 기존 레시피 확인
            query = select(Recipe).where(Recipe.recipe_id == recipe_id)
            result = await session.execute(query)
            existing_recipe = result.scalar_one_or_none()
            
            # 재료, 조리순서 추출
            material_names = self._parse_materials(recipe_data.get('RCP_PARTS_DTLS', ''))
            instructions = self._extract_instructions(recipe_data)

            # 썸네일 이미지를 S3에 업로드
            thumbnail_original_url = recipe_data.get('ATT_FILE_NO_MK', '').strip()
            thumbnail_s3_url = await s3_helper.upload_thumbnail_from_url(
                thumbnail_original_url,
                recipe_id
            )
            # S3 업로드 실패 시 원본 URL 사용
            thumbnail_url = thumbnail_s3_url if thumbnail_s3_url else thumbnail_original_url

            # 조리 과정 이미지를 S3에 업로드 (MANUAL_IMG01~MANUAL_IMG20)
            manual_image_s3_urls = []
            for i in range(1, 21):
                key = f"MANUAL_IMG{i:02d}" if i >= 10 else f"MANUAL_IMG0{i}"
                img_url = recipe_data.get(key, '').strip()
                if img_url:
                    s3_url = await s3_helper.upload_image_from_url(img_url, recipe_id, i)
                    if s3_url:
                        manual_image_s3_urls.append(s3_url)
            
            # UPSERT: 기존 레시피가 있으면 UPDATE, 없으면 INSERT
            if existing_recipe:
                # 기존 이미지 삭제 (새 이미지로 교체)
                if manual_image_s3_urls:  # 새 이미지가 있을 때만 삭제
                    s3_helper.delete_recipe_images(recipe_id)

                # 업데이트
                existing_recipe.recipe_name = name
                existing_recipe.recipe_pat = recipe_pat
                existing_recipe.method = method
                existing_recipe.thumbnail_url = thumbnail_url
                existing_recipe.instructions = instructions
                existing_recipe.material_names = material_names
                existing_recipe.image_url = manual_image_s3_urls

                # 명시적으로 flush (롤백 상태 방지)
                await session.flush()
                return existing_recipe
            else:
                # 새로 생성
                new_recipe = Recipe(
                    recipe_id=recipe_id,
                    recipe_pat=recipe_pat,
                    method=method,
                    recipe_name=name,
                    thumbnail_url=thumbnail_url,
                    instructions=instructions,
                    material_names=material_names,
                    image_url=manual_image_s3_urls
                )
                session.add(new_recipe)
                await session.flush()  # 명시적으로 flush
                return new_recipe
                
        except Exception as e:
            print(f"Failed to sync recipe {recipe_data.get('RCP_SEQ')}: {str(e)}")
            return None
    
    async def sync_all_recipes(
            self,
            session: AsyncSession,
            batch_size: int = 500,
            use_incremental: bool = True
    ):
        """
        모든 레시피를 동기화
        
        Args:
            session: DB 세션
            batch_size: 한 번에 가져올 레시피 수
            use_incremental: True이면 마지막 동기화 이후 변경된 레시피만 가져옴
        """
        change_date = None
        if use_incremental:
            change_date = self._get_last_sync_date()
            print(f"Syncing recipes chagned after: {change_date}")

        start = 1
        total_synced = 0
        
        while True:
            end = start + batch_size - 1
            print(f"Fetching recipes {start} to {end}...")
            
            recipes = await self.fetch_recipes_from_api(start, end, change_date)
            
            if not recipes:
                break
            
            # 각 레시피 동기화 (개별 커밋으로 롤백 에러 방지)
            for recipe_data in recipes:
                try:
                    result = await self.sync_recipe(session, recipe_data)
                    if result:
                        # 각 레시피마다 개별 커밋 (IntegrityError 방지)
                        await session.commit()
                        total_synced += 1
                except Exception as e:
                    # 에러 발생 시 롤백 후 다음 레시피 계속 처리
                    await session.rollback()
                    recipe_id = recipe_data.get('RCP_SEQ', 'unknown')
                    print(f"Failed to sync recipe {recipe_id}, rolled back: {str(e)}")

            print(f"Synced {total_synced} recipes in this batch (Total: {total_synced})")
            
            # 다음 배치로
            if len(recipes) < batch_size:
                break
            start = end + 1
        
        if use_incremental and total_synced > 0:
            today = datetime.now().strftime('%Y%m%d')
            self._update_last_sync_date(today)
            print(f"Updated last sync date to: {today}")
        
        print(f"Sync completed. Total synced: {total_synced} recipes")
        return total_synced


recipe_sync_service = RecipeSyncService()