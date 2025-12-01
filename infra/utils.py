import os

Config = {
  "Production": os.getenv("ENV") == "production",
  "Account": os.getenv("AWS_ACCOUNT_ID"),
  "Region": os.getenv("AWS_REGION"),

  # Materials 서비스 설정
  "Materials": {
    # 기존 EIP 정보 (새 EC2 인스턴스에 연결)
    "eip_allocation_id": "eipalloc-030258a8cefacdd5e",
    "eip_address": "52.78.138.82"
  },

  # Recipe 서비스 설정
  "Recipe": {
    "timeout_minutes": 15, # Lambda 레시피 동기화 시간
    "memory_size": 1024 # Lambda Memory Size
  }
}
