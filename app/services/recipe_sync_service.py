import re
from typing import List, Dict, Optional
import httpx
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.config import settings
from models.recipes import Recipe
from utils.s3_helper import s3_helper


class RecipeSyncService:
    def __init__(self):
        self.api_key = settings.FOOD_SAFETY_API_KEY
        self.base_url = settings.FOOD_SAFETY_API_BASE_URL
    
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
    
    def _extract_image_urls(self, recipe_data: Dict) -> List[str]:
        """
        MANUAL_IMG01~MANUAL_IMG20과 ATT_FILE_NO_MAIN, ATT_FILE_NO_MK에서 이미지 URL 추출
        """
        image_urls = []
        
        # 메인 이미지 먼저 추가 (요리 썸네일)
        mk_img = recipe_data.get('ATT_FILE_NO_MK', '').strip()
        if mk_img and mk_img not in image_urls:
            image_urls.append(mk_img)
        
        # 매뉴얼 이미지들 추가
        for i in range(1, 21):
            key = f"MANUAL_IMG{i:02d}" if i >= 10 else f"MANUAL_IMG0{i}"
            img_url = recipe_data.get(key, '').strip()
            if img_url and img_url not in image_urls:
                image_urls.append(img_url)
        
        return image_urls
    
    async def fetch_recipes_from_api(self, start: int = 1, end: int = 999) -> List[Dict]:
        """
        식품의약품안전처 API에서 레시피 데이터 가져오기
        
        Args:
            start: 시작 인덱스
            end: 끝 인덱스 (최대 999개씩 가능)
        """
        url = f"{self.base_url}/{self.api_key}/COOKRCP01/json/{start}/{end}"
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                # API 응답 구조: {serviceId: {total_count: ..., row: [...]}}
                service_id = 'COOKRCP01'
                if service_id in data and 'row' in data[service_id]:
                    return data[service_id]['row']
                return []
        except Exception as e:
            print(f"Failed to fetch recipes from API: {str(e)}")
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
            
            # 재료, 조리순서, 이미지 URL 추출
            material_names = self._parse_materials(recipe_data.get('RCP_PARTS_DTLS', ''))
            instructions = self._extract_instructions(recipe_data)
            images = self._extract_image_urls(recipe_data)
            thumbnail_url = images[0]
            image_urls = images[1:]
            
            # 이미지 URL을 S3에 업로드
            s3_image_urls = []
            for idx, img_url in enumerate(image_urls):
                s3_url = await s3_helper.upload_image_from_url(img_url, recipe_id, idx+1) # 1번 idx부터
                if s3_url:
                    s3_image_urls.append(s3_url)
            
            if existing_recipe:
                # 기존 이미지 삭제 (새 이미지로 교체)
                if s3_image_urls:  # 새 이미지가 있을 때만 삭제
                    s3_helper.delete_recipe_images(recipe_id)
                
                # 업데이트
                existing_recipe.name = name
                existing_recipe.recipe_pat = recipe_pat
                existing_recipe.method = method
                existing_recipe.thumbnail_url = thumbnail_url
                existing_recipe.instructions = instructions
                existing_recipe.material_names = material_names
                existing_recipe.image_url = s3_image_urls
                
                session.add(existing_recipe)
                return existing_recipe
            else:
                # 새로 생성
                new_recipe = Recipe(
                    recipe_id=recipe_id,
                    recipe_pat=recipe_pat,
                    method=method,
                    name=name,
                    thumbnail_url=thumbnail_url,
                    instructions=instructions,
                    material_names=material_names,
                    image_url=s3_image_urls
                )
                session.add(new_recipe)
                return new_recipe
                
        except Exception as e:
            print(f"Failed to sync recipe {recipe_data.get('RCP_SEQ')}: {str(e)}")
            return None
    
    async def sync_all_recipes(self, session: AsyncSession, batch_size: int = 500):
        """
        모든 레시피를 동기화
        
        Args:
            session: DB 세션
            batch_size: 한 번에 가져올 레시피 수
        """
        start = 1
        total_synced = 0
        
        while True:
            end = start + batch_size - 1
            print(f"Fetching recipes {start} to {end}...")
            
            recipes = await self.fetch_recipes_from_api(start, end)
            
            if not recipes:
                break
            
            # 각 레시피 동기화
            for recipe_data in recipes:
                result = await self.sync_recipe(session, recipe_data)
                if result:
                    total_synced += 1
            
            # 배치 커밋
            await session.commit()
            print(f"Synced {len(recipes)} recipes (Total: {total_synced})")
            
            # 다음 배치로
            if len(recipes) < batch_size:
                break
            start = end + 1
        
        print(f"Sync completed. Total synced: {total_synced} recipes")
        return total_synced


recipe_sync_service = RecipeSyncService()