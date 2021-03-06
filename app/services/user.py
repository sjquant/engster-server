from typing import Optional, Dict, Any
import secrets
import random
import uuid

from app.models import User, Translation
from app.utils import get_file_url
from app.exceptions import DataDoesNotExist
from app import config, db


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


async def get_activitiy_summary(user_id: uuid.UUID) -> Dict[str, Any]:
    query = (
        db.select([User.nickname, User.photo, db.func.count(Translation.id)])
        .select_from(User.outerjoin(Translation))
        .where(User.id == user_id)
        .group_by(User.id)
    )
    data = await query.gino.first()
    if data:
        data = {
            "user_id": user_id,
            "user_nickname": data[0],
            "user_photo": get_file_url(data[1], file_host=config.MEDIA_URL),
            "translation_count": data[2],
        }
    else:
        raise DataDoesNotExist("User activity summary not found")
    return data
