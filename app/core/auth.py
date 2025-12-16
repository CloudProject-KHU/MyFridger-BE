from fastapi import Depends, HTTPException, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import requests
from jose import JWTError, jwt

from app.models.user import User

from .config import settings

JWKS_URL = f"{settings.AWS_COGNITO_USER_POOL}/.well-known/jwks.json"
jwks = requests.get(JWKS_URL).json()


def get_token_key(token: str):
    headers = jwt.get_unverified_header(token)
    kid = headers["kid"]
    for key in jwks["keys"]:
        if key["kid"] == kid:
            return key

    raise Exception("Matching JWK not found")


def decode_access_token(token: str):
    try:
        key = get_token_key(token)
        payload = jwt.decode(token, key)

        return payload  # dict
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )


bearer_scheme = HTTPBearer(auto_error=False)
def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> User:
    token = credentials.credentials if credentials else None
    print("Authorizing token:", token, credentials)

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing",
        )

    payload = decode_access_token(token)

    id = payload.get("sub")
    username = payload.get("username")

    if not id or not username:
        raise HTTPException(
            status_code=401,
            detail="Invalid token payload",
        )

    return User(id, username)
