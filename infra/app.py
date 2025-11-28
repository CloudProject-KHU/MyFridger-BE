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

# 1. 공통 리소스 스택 (VPC, 공유 RDS, S3, Secrets, CloudWatch)
common_stack = CommonStack(app, "MyFridger-Common")

# 2. Materials 서비스 스택 (EC2 API, 공유 RDS 사용)
materials_stack = MaterialsStack(
    app,
    "MyFridger-Materials",
    vpc=common_stack.vpc,
    db_instance=common_stack.db_instance,
    db_security_group=common_stack.db_security_group,
)
materials_stack.add_dependency(common_stack)

# 3. Recipe 서비스 스택 (Lambda + EventBridge, 공유 RDS 및 S3 사용)
recipe_stack = RecipeStack(
    app,
    "MyFridger-Recipe",
    vpc=common_stack.vpc,
    db_instance=common_stack.db_instance,
    db_security_group=common_stack.db_security_group,
    uploads_bucket=common_stack.uploads_bucket,
    food_safety_api_secret=common_stack.food_safety_api_secret,
    recipe_sync_metadata_secret=common_stack.recipe_sync_metadata_secret,
)
recipe_stack.add_dependency(common_stack)

# 4. Alerts 서비스 스택 (TODO: 구현 필요, 공유 RDS 사용 예정)
# alerts_stack = AlertsStack(
#     app,
#     "MyFridger-Alerts",
#     vpc=common_stack.vpc,
#     db_instance=common_stack.db_instance,
#     db_security_group=common_stack.db_security_group,
# )
# alerts_stack.add_dependency(common_stack)

# 5. Users 서비스 스택 (TODO: 구현 필요, 공유 RDS 사용 예정)
# users_stack = UsersStack(
#     app,
#     "MyFridger-Users",
#     vpc=common_stack.vpc,
#     db_instance=common_stack.db_instance,
#     db_security_group=common_stack.db_security_group,
# )
# users_stack.add_dependency(common_stack)

# ==============================================
# 기존 통합 백엔드 스택 (레거시, 참고용으로 유지)
# ==============================================
backend_stack = BackendStack(app, "FridgerBackend")

app.synth()
