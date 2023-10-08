"""Defines authentication functions."""

import bcrypt


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("ascii"), bcrypt.gensalt(12)).decode("ascii")


def check_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("ascii"), hashed_password.encode("ascii"))
