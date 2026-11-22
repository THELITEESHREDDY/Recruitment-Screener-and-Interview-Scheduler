import os

import jwt
from jwt.exceptions import InvalidTokenError

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy.orm import Session

from shared.config import settings
from backend.db.connection import get_db
from backend.models.users import User



bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db)
) -> User:

    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"}
    )

    if credentials is None:
        raise credentials_error

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            settings.JWT_ALGORITHM
        )

        user_id = payload.get("sub")

        if not isinstance(user_id, str) or not user_id:
            raise credentials_error

    except InvalidTokenError:
        raise credentials_error

    user = db.get(User, user_id)

    if user is None:
        raise credentials_error

    return user