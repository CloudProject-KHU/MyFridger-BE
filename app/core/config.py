from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # General
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: str

    # AWS
    AWS_REGION: str = "ap-northeast-2"  # 서울 리전 (기본)

    # S3
    S3_BUCKET_NAME: str = ""  # CDK에서 생성된 버킷 이름
    S3_RECIPE_PREFIX: str = "recipes"  # 레시피 이미지 저장 경로

    # Amazon Bedrock (Nova Lite)
    BEDROCK_REGION: str = "ap-northeast-2"  # Amazon Nova Lite 지원 리전 (서울)

    # Food Safety Korea API
    FOOD_SAFETY_API_KEY: str = ""
    FOOD_SAFETY_API_BASE_URL: str = "http://openapi.foodsafetykorea.go.kr/api"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"


settings = Settings()
