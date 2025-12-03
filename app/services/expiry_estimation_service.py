from datetime import datetime, timedelta
from typing import Dict, Optional
import json
import boto3

from app.core.config import settings
from app.models.recipes import ExpiryEstimationRequest, ExpiryEstimationResponse


# 카테고리별 기본 소비기한 규칙 (일 단위)
EXPIRY_RULES: Dict[str, Dict] = {
  "vegetable": {
    "min_days": 3,
    "max_days": 30,
    "default": 10
  },
  "fruit": {
    "min_days": 2,
    "max_days": 14,
    "default": 7
  },
  "meat": {
    "min_days": 2,
    "max_days": 56,
    "default": 4
  },
  "seafood": {
    "min_days": 1,
    "max_days": 3,
    "default": 2
  },
  "dairy_processed": {
    "min_days": 7,
    "max_days": 35,
    "default": 18
  },
  "seasoning": {
    "min_days": 180,
    "max_days": 365,
    "default": 270
  },
  "homemade": {
    "min_days": 2,
    "max_days": 7,
    "default": 4
  },
  "etc": {
    "min_days": 0,
    "max_days": 0,
    "default": 0
  }
}


class ExpiryEstimationService:
    """소비기한 추정 서비스"""

    def __init__(self, bedrock_client): # Amazon Bedrock 클라이언트 생성을 싱글톤으로 early loading.
        self._bedrock_client = bedrock_client

    # def _get_bedrock_client(self):
    #     """Amazon Bedrock 클라이언트 생성 (lazy loading)"""
    #     if self._bedrock_client is None:
    #         try:
    #             self._bedrock_client = boto3.client(
    #                 'bedrock-runtime',
    #                 region_name=settings.BEDROCK_REGION  # Amazon Bedrock (Nova Lite) 지원 리전 사용
    #             )
    #         except Exception as e:
    #             print(f"Failed to create Bedrock client: {str(e)}")
    #             self._bedrock_client = None
    #     return self._bedrock_client

    def estimate_expiry_rule_based(
        self,
        request: ExpiryEstimationRequest
    ) -> ExpiryEstimationResponse:
        """
        Option A: Rule-Based Estimation
        카테고리별 기본 소비기한 규칙을 사용한 추정
        """
        name_lower = request.name.lower()
        category_lower = request.category.lower()

        # 우선순위 1: 재료 이름으로 직접 매칭
        rule = None
        for key, value in EXPIRY_RULES.items():
            if key.lower() in name_lower:
                rule = value
                break

        # 우선순위 2: 카테고리로 매칭
        if not rule:
            for key, value in EXPIRY_RULES.items():
                if key.lower() in category_lower:
                    rule = value
                    break

        # 우선순위 3: 기본값
        if not rule:
            rule = EXPIRY_RULES["etc"]

        # 소비기한 계산(default값 사용)
        estimated_days = rule["default"]
        estimated_date = request.purchased_at + timedelta(days=estimated_days)

        # 신뢰도 계산 (규칙 기반이므로 중간 수준)
        confidence = 0.5 if rule != EXPIRY_RULES["etc"] else 0.0

        notes = f"냉장 보관 시 평균 {estimated_days}일 기준 (최소 {rule["min_days"]}일, 최대 {rule["max_days"]}일) (규칙 기반 추정)"

        return ExpiryEstimationResponse(
            estimated_expiration_date=estimated_date,
            confidence=confidence,
            notes=notes
        )

    async def estimate_expiry_ai_based(
        self,
        request: ExpiryEstimationRequest
    ) -> ExpiryEstimationResponse:
        """
        Option B: Amazon Bedrock (Nova Lite) 기반 추정
        AI를 활용한 더 정교한 소비기한 추정
        """

        if not self._bedrock_client:
            # Bedrock 사용 불가 시 규칙 기반으로 폴백
            return self.estimate_expiry_rule_based(request)

        try:
            # Amazon Nova Lite에게 보낼 프롬프트 구성
            prompt = f"""당신은 시중에서 판매되는 식품과 식재료, 혹은 조리된 가정식 음식의 소비기한 또는 안전 보관 가능 기간을 추정하는 식품 안전 보조 모델입니다. 

정확한 법적 소비기한을 제공하는 것이 아니라,
입력된 텍스트를 분석하여 “식품 유형 → 위험도 → 보관 방식 → 소비/보관 가능 기간”을 식품의약품안전처(MFDS) 및 한국식품산업협회 소비기한 연구센터의 공식 참고값을 기준으로 추정해야 합니다.

---

## 1. 입력 분석: 두 경우 중 하나로 자동 분류

입력된 설명을 NLP로 분석하여 다음 중 어떤 유형인지 판단하십시오.

1. **시중 식품 / 식재료**  
→ 가공 정도, 저장 방식, 유통 시차(제조~진열~구매)를 고려하여 소비기한 추정

2. **가정식 조리 음식(반찬/요리)**  
→ 조리 방식, 원재료, 수분 함량, 부패 위험도 기반으로 보관 가능 기간 추정

둘 중 어느 경우인지 먼저 분류하고, 그에 맞는 규칙을 적용하세요.

---

## 2. 시중 식품(상업 제품) 추정 규칙

### 2-1. 추론 요소
- 식품 유형(육류/채소/유제품/두부/빵/냉동/즉석 등)
- 가공 정도: 신선 / 반가공 / 완전가공
- 보관 방식: 상온/냉장/냉동
- 수분 함량 및 부패 위험도

### 2-2. 일반 소비기한 패턴 (식약처 소비기한 설정보고서 8차 기준, 2025년)
#### 신선 식품군
- **신선 육류·생선**: 냉장 1~3일
  - 소고기: 3~5일 (소비기한 참고값)
  - 돼지고기: 3~5일 (소비기한 참고값)
  - 닭고기: 2~3일 (소비기한 참고값)
  - 생선: 1~2일 (소비기한 참고값)

- **신선 해산물**: 냉장 1~3일
  - 조개/게/새우/오징어: 1~2일
  - 건조 해산물(미역 등): 냉실 보관 30~90일

- **신선 채소**: 냉장 3~30일
  - 상추/버섯 등 빨리 상하는 채소: 3~5일
  - 배추/무/고추 등 중기 보관 채소: 7~14일
  - 당근/감자/양파 등 장기 보관 채소: 14~30일
  - 마늘(냉장): 60~90일
  - 김치: 14~35일

- **신선 과일**: 냉장 2~21일
  - 딸기: 2~3일
  - 바나나: 3~5일 (냉장 시)
  - 포도/수박 등: 5~10일
  - 사과/배/귤/레몬 등: 7~21일

#### 유제품 / 반가공 식품군
- **우유**: 냉장 7~10일 (식약처 참고값: 평균 7일)
- **발효유·요거트**: 냉장 7~32일 (식약처 참고값: 18~32일)
- **가공유(딸기우유 등)**: 냉장 16~24일 (식약처 참고값)
- **치즈**: 냉장 14~30일
- **계란/달걀**: 냉장 14~21일 (식약처 참고값: 18일 평균)
- **두부**: 냉장 21~35일 (식약처 참고값: 23일 평균)
- **만두(냉동)**: 냉동 60~90일

#### 육류 가공식품
- **햄**: 냉장 38~57일 (식약처 참고값)
- **소시지**: 냉장 39~56일 (식약처 참고값: 48일 평균)
- **어묵**: 냉장 29~42일 (식약처 참고값: 35일 평균)

#### 빵·베이커리
- **빵류**: 냉장/상온 3~54일 (식약처 참고값 범위)
  - 일반 빵: 2~5일
  - 식빵(냉장): 3~20일
  - 샌드위치: 1~2일

#### 음료·액체
- **과채주스**: 냉장 20~35일 (식약처 참고값)
- **혼합음료(초콜릿 음료 등)**: 냉장/상온 60~180일 (식약처 참고값)
- **기타 음료**: 상온 7~30일

#### 냉동식품
- **냉동 식품(일반)**: 냉동 30~90일 (약 1~3개월)
- **냉동 생선**: 냉동 30~90일

#### 건조·장류·양념 (상온 보관)
- **라면**: 상온 92~183일 (식약처 참고값)
- **과자/스낵**: 상온 90~174일
- **간장**: 상온 180~365일 (식약처 참고값)
- **고추장/된장**: 상온 180~365일
- **참기름**: 상온 180~365일
- **케첩/머스터드**: 상온 180~365일
- **소금/설탕**: 상온 무제한 (1년 이상)

#### 캔/병 식품
- **참치캔**: 상온 3~10년 (냉실 보관 시 더 장기)

### 2-3. 유통 시차 추정

- 제조→매장 진열 걸리는 시간: 1~5일
→ 구매일로부터 제조일(추정) 역산 후 소비기한 추정

---

## 3. 가정식 조리 음식 추정 규칙

### 3-1. 추론 요소
- 조리 방식(볶음, 무침, 찌개, 조림 등)
- 단백질 포함 여부
- 수분 함량
- 위험도 평가

### 3-2. 일반 보관 기간 규칙 (냉장 기준)

#### 고위험군 (냉장 1~3일)
- 수분 많고 단백질 포함 음식: 탕, 찌개, 국, 볶음류
  - 냉장: 1~3일
  - 냉동: 2~4주 (단, 식감 저하)

- 조리된 육류/생선:
  - 냉장: 2~3일
  - 냉동: 2~4주

- 튀김류:
  - 냉장: 1~2일 (식감 저하 고려)

#### 중위험군 (냉장 1~2일)
- 조리된 채소 반찬(나물, 무침):
  - 냉장: 1~2일
  - 상온(여름): 수시간 이내

#### 저위험군 (냉장 3~5일)
- 양념·간장 위주의 조림류:
  - 냉장: 3~5일

- 계란말이:
  - 냉장: 1~2일

#### 초저위험군 (냉장 1주~수개월)
- 김치 등 발효 기반 (조리 여부에 따라 상이):
  - 냉장: 2주~수개월 (조리김치는 1~2주)
  - 발효김치: 냉장 1개월 이상

- 염장/절임:
  - 냉장: 1주~수개월

- 냉동 저장 반찬:
  - 냉동: 2~4주
  - 점진적 식감 저하

### 3-3. 상온 보관 (여름/겨울 구분)

- 여름(실온 20~25°C 이상):
  - 고위험군: 2~4시간 이내
  - 중위험군: 4~8시간 이내

- 겨울(실온 10°C 이하):
  - 고위험군: 8~12시간 이내
  - 중위험군: 12~24시간 이내

---

## 4. 출력 형식 (JSON)

{
    "estimated_days": <예상 소비기한 일수(integer)>,
    "confidence": <신뢰도 0.0~1.0 (float),
                          정보 부족 시 0.6~0.7,
                          일반적인 경우 0.8~0.9,
                          공식 참고값 정확 매칭 시 0.95~1.0>,
    "notes": "<추정 근거 및 보관 팁 (string), 권장 보관 방법도 포함>"
}

---

## 5. 입력
- 음식명 또는 재료명: {request.name}
- 카테고리: {request.category}
- 구매 혹은 조리 날짜: {request.purchased_at.strftime('%Y-%m-%d')}

---

위 기준에 따라 소비기한 또는 안전 보관 기간을 추정하십시오.
"""

            # Bedrock API 호출 (Amazon Nova Lite 형식)
            response = self._bedrock_client.invoke_model(
                modelId="amazon.nova-lite-v1:0",
                body=json.dumps({
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "text": prompt
                                }
                            ]
                        }
                    ],
                    "inferenceConfig": {
                        "max_new_tokens": 500,
                        "temperature": 0.7,
                        "top_p": 0.9
                    }
                })
            )

            # 응답 파싱 (Amazon Nova 형식)
            response_body = json.loads(response['body'].read())
            content = response_body['output']['message']['content'][0]['text']

            # JSON 추출 (Nova가 추가 텍스트를 포함할 수 있으므로)
            import re
            json_match = re.search(r'\{[^{}]*\}', content)
            if json_match:
                ai_result = json.loads(json_match.group())

                estimated_days = ai_result.get("estimated_days", 7)
                confidence = ai_result.get("confidence", 0.8)
                notes = ai_result.get("notes", "AI 기반 추정")

                estimated_date = request.purchased_at + timedelta(days=estimated_days)

                return ExpiryEstimationResponse(
                    estimated_expiration_date=estimated_date,
                    confidence=confidence,
                    notes=notes
                )
            else:
                raise ValueError("Invalid AI response format")

        except Exception as e:
            print(f"AI-based estimation failed: {str(e)}")
            # AI 실패 시 규칙 기반으로 폴백
            return self.estimate_expiry_rule_based(request)

    async def estimate_expiry(
        self,
        request: ExpiryEstimationRequest,
        use_ai: bool = True
    ) -> ExpiryEstimationResponse:
        """
        소비기한 추정 (AI 또는 규칙 기반)

        Args:
            request: 추정 요청 정보
            use_ai: True면 AI 기반, False면 규칙 기반 (기본값: True)

        Returns:
            추정된 소비기한 정보
        """
        # 개발 환경에서는 규칙 기반만 사용
        if not use_ai: # or settings.ENVIRONMENT == "development":
            return self.estimate_expiry_rule_based(request)

        # 프로덕션에서는 AI 사용 (실패 시 규칙 기반 폴백)
        return await self.estimate_expiry_ai_based(request)


# expiry_estimation_service = ExpiryEstimationService()