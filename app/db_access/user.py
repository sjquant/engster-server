from typing import Optional
import secrets
import random
import uuid

from app.db_models import User


def generate_random_characters(prefix_length=4, suffix_length=6):
    """generate random nickname when user didn't enter nickname"""
    allowed_prefix_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    allowed_suffix_chars = "abcdefghizklmnopqrstuvwxyz0123456789!@#$%^&*="

    prefix = "".join(secrets.choice(allowed_prefix_chars) for i in range(prefix_length))
    suffix = "".join(secrets.choice(allowed_suffix_chars) for i in range(suffix_length))
    return prefix + suffix


async def get_user_by_email(email: str) -> User:
    """Get user by email"""
    user = await User.query.where(User.email == email).gino.first()
    return user


async def get_user_by_id(user_id: str) -> User:
    """Get user by id"""
    user = await User.query.where(User.id == user_id).gino.first()
    return user


async def create_user(
    email: str,
    password: Optional[str] = None,
    nickname: Optional[str] = None,
    photo: Optional[str] = None,
    is_admin: bool = False,
) -> User:
    """Create User"""
    id_ = uuid.uuid4()
    nickname = nickname or generate_random_characters(
        prefix_length=4, suffix_length=random.randint(1, 6)
    )
    user = User(id=id_, email=email, nickname=nickname, photo=photo, is_admin=is_admin)
    user.set_password(password)
    await user.create()
    return user
