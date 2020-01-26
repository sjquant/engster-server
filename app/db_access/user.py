from app.db_models import User


async def get_user_by_email(email: str) -> User:
    """ get like count for lines """
    user = await User.query.where(User.email == email).gino.first()
    return user


async def get_user_by_id(user_id: str) -> User:
    """ get like count for lines """
    user = await User.query.where(User.id == user_id).gino.first()
    return user
