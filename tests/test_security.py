
from app.core.security import hash_password, verify_password


def test_hash_password_does_not_return_plain_password():
    password = "StrongPassword123!"

    hashed_password = hash_password(password)

    assert hashed_password != password
    assert hashed_password.startswith("$argon2")


def test_verify_password_with_correct_password():
    password = "StrongPassword123!"
    hashed_password = hash_password(password)

    assert verify_password(password, hashed_password) is True


def test_verify_password_with_incorrect_password():
    hashed_password = hash_password("StrongPassword123!")

    assert verify_password("WrongPassword123!", hashed_password) is False
