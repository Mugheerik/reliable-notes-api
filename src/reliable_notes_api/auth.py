from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from sqlalchemy.orm import Session
from uuid import UUID
from reliable_notes_api.database import get_db
from reliable_notes_api.models import User
from reliable_notes_api.security import decode_access_token

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        token = credentials.credentials
        user_id = UUID(decode_access_token(token))

    except (ValueError, TypeError,jwt.InvalidTokenError, jwt.ExpiredSignatureError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )

    user = db.get(User, user_id)

    print("DATABASE USER:", user)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="Invalid or inactive user",
        )

    return user