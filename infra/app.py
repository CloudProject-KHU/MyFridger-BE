import aws_cdk as cdk

from stacks import (
    CommonStack,
    MaterialsStack,
    RecipeStack,
    AlertsStack,
    UsersStack,
    BackendStack,
)
from utils import Config

app = cdk.App()

# ==============================================
# 새로운 마이크로서비스 아키텍처 (단일 RDS with 다중 데이터베이스)
# ==============================================

# 1. 공통 리소스 스택
backend_stack = BackendStack(app, "FridgerBackend")

# 2. Recipe 서비스 스택 (Lambda + EventBridge, 공유 RDS 및 S3 사용)
recipe_stack = RecipeStack(
    app,
    "MyFridger-Recipe",
    vpc=backend_stack.vpc,
    db_instance=backend_stack.db_instance,
    db_security_group=backend_stack.db_security_group,
    uploads_bucket=backend_stack.uploads_bucket,
    food_safety_api_secret=backend_stack.food_safety_api_secret,
    recipe_sync_metadata_secret=backend_stack.recipe_sync_metadata_secret,
)
recipe_stack.add_dependency(backend_stack)

app.synth()
