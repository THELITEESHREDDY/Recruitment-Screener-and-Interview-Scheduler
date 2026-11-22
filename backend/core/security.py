from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from shared.config import settings
from datetime import datetime, timedelta, timezone
import jwt


password_hasher = PasswordHasher()





def create_access_token(user_id: str) -> str:
    secret_key = settings.JWT_SECRET_KEY

    expires_in = int(
        settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )

    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=expires_in
    )

    return jwt.encode(
        {
            "sub": user_id,
            "exp": expires_at,
        },
        secret_key,
        algorithm="HS256"
    )

def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    try:
        return password_hasher.verify(
            hashed_password,
            plain_password
        )
    except (VerifyMismatchError, VerificationError):
        return False