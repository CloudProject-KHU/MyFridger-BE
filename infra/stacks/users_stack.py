"""
Users Stack - 사용자 인증 및 관리 서비스 (구조 및 설명)

Cognito 인증:
- Amazon Cognito (사용자 인증/인가)
- Cognito User Pool
- Cognito Identity Pool
- OAuth 2.0 Social Login (Google, Kakao 등)
- CommonStack의 공유 RDS 사용

주요 기능:
1. Cognito Hosted UI를 통한 소셜 로그인
2. JWT 토큰 발급 및 검증
3. Users 테이블에 사용자 정보 저장/업데이트
4. Refresh Token 관리
5. API Gateway Authorizer 통합

테이블 스키마:
- users: 사용자 기본 정보
  - id, cognito_sub, email, name, image_url, provider
  - created_at, updated_at, last_login_at
- refresh_tokens: Refresh Token 관리
  - id, user_id, token_hash, expires_at, revoked_at
"""
from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_cognito as cognito,
)
from constructs import Construct
from utils import Config


class UsersStack(Stack):
    """
    사용자 인증 및 관리 서비스 스택

    Dependencies:
    - CommonStack (VPC, 공유 RDS)

    Resources:
    - Cognito User Pool (사용자 풀)
    - Cognito User Pool Client (앱 클라이언트)
    - Cognito Identity Pool (자격 증명 풀)
    - Cognito Identity Providers (Google, Kakao 등)

    Database:
    - CommonStack의 공유 RDS 인스턴스 사용
    - Database: myfridger_db
    - Tables: users, refresh_tokens

    Cognito 설정:
    - OAuth 2.0 Authorization Code Flow
    - Social Identity Providers: Google, Kakao, Apple
    - Hosted UI: /oauth2/authorize, /oauth2/token
    - Callback URLs: https://yourdomain.com/auth/callback
    - Token Validity:
      - ID Token: 1 hour
      - Access Token: 1 hour
      - Refresh Token: 30 days

    API 인증 플로우:
    1. 클라이언트 -> Cognito Hosted UI 리다이렉트
    2. 소셜 로그인 (Google/Kakao 등)
    3. Cognito -> Callback URL (Authorization Code)
    4. FastAPI -> Cognito Token Endpoint (Code -> Tokens)
    5. FastAPI -> 공유 DB Users 테이블에 사용자 정보 저장/업데이트
    6. FastAPI -> 자체 JWT 발급 (Optional)
    7. 이후 API 요청 시 JWT를 Authorization 헤더로 전송
    8. API Gateway Authorizer가 JWT 검증

    RDS 연결:
    - FastAPI Auth Service에서 공유 RDS에 접근
    - Cognito Sub를 기준으로 사용자 매핑
    - 첫 로그인 시 Users 테이블에 레코드 생성
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.IVpc,
        db_instance: rds.IDatabaseInstance,
        db_security_group: ec2.ISecurityGroup,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # TODO: 구현 필요
        # 1. Cognito User Pool 생성
        #    - Email/Password 인증 활성화
        #    - MFA 설정 (Optional)
        #    - Password Policy 설정
        # 2. Cognito User Pool Client 생성
        #    - OAuth 2.0 Flows: Authorization Code Grant
        #    - Allowed Scopes: openid, email, profile
        #    - Callback URLs, Logout URLs 설정
        # 3. Cognito Identity Providers 설정
        #    - Google OAuth 2.0
        #    - Kakao OAuth 2.0
        #    - Apple Sign In
        # 4. Cognito Identity Pool 생성 (Optional)
        #    - AWS 리소스 직접 접근 시 사용
        # 5. Outputs 설정
        #    - User Pool ID
        #    - User Pool Client ID
        #    - User Pool Domain
        #    - Identity Pool ID

        pass


# FastAPI Auth Service 예시 구조:
"""
app/api/auth.py

@router.get("/callback")
async def auth_callback(
    code: str,
    state: str,
    redirect_uri: str,
    session: AsyncSession = Depends(get_session)
):
    # Step 1: Authorization Code를 Tokens로 교환
    token_response = await cognito_client.exchange_code_for_tokens(
        code=code,
        redirect_uri=redirect_uri
    )

    id_token = token_response["id_token"]
    access_token = token_response["access_token"]
    refresh_token = token_response["refresh_token"]

    # Step 2: ID Token 디코드 및 검증
    user_info = decode_jwt(id_token)
    cognito_sub = user_info["sub"]
    email = user_info["email"]
    name = user_info.get("name")

    # Step 3: Users DB에서 사용자 조회/생성
    user = await get_or_create_user(
        session=session,
        cognito_sub=cognito_sub,
        email=email,
        name=name
    )

    # Step 4: 자체 JWT 발급 (Optional)
    app_jwt = generate_app_jwt(user_id=user.id)

    # Step 5: Refresh Token 저장
    await save_refresh_token(
        session=session,
        user_id=user.id,
        token=refresh_token
    )

    # Step 6: 클라이언트로 리다이렉트
    return RedirectResponse(
        url=f"{redirect_uri}?access_token={app_jwt}&refresh_token={refresh_token}"
    )


@router.post("/token-refresh")
async def refresh_access_token(
    refresh_token: str,
    session: AsyncSession = Depends(get_session)
):
    # Step 1: Refresh Token 검증
    token_record = await get_refresh_token(session, refresh_token)

    if not token_record or token_record.revoked_at or token_record.is_expired():
        raise HTTPException(401, "Invalid or expired refresh token")

    # Step 2: 기존 토큰 무효화
    await revoke_refresh_token(session, token_record.id)

    # Step 3: 새로운 토큰 발급
    new_access_token = generate_app_jwt(user_id=token_record.user_id)
    new_refresh_token = generate_refresh_token()

    # Step 4: 새로운 Refresh Token 저장
    await save_refresh_token(
        session=session,
        user_id=token_record.user_id,
        token=new_refresh_token
    )

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "expires_in": 3600
    }
"""
