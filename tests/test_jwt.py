
import jwt

from app.core.config import settings
from app.core.security import create_access_token


def test_create_access_token():
    user_id = 20

    token = create_access_token(
        subject=str(user_id),
    )

    payload = jwt.decode(
        token,
        settings.secret_key,
        algorithms=["HS256"],
    )

    assert payload["sub"] == str(user_id)
    assert "iat" in payload
    assert "exp" in payload
