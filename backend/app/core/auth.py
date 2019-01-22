from sanic_jwt import exceptions
from app.models import User


async def authenticate(request, *args, **kwargs):
    """ authenticate user """
    username = request.json.get("email", None)
    password = request.json.get("password", None)

    if not username or not password:
        raise exceptions.AuthenticationFailed("Missing username or password.")

    user = await User.query.where(User.email == username).gino.first()
    if user is None:
        raise exceptions.AuthenticationFailed("User not found.")

    if not user.check_password(password):
        raise exceptions.AuthenticationFailed("Password is incorrect.")

    return user


# async def store_refresh_token(user_id, refresh_token, *args, **kwargs):
#     key = f'refresh_token_{user_id}'
#     await aredis.set(key, refresh_token)


# async def retrieve_refresh_token(request, user_id, *args, **kwargs):
#     key = f'refresh_token_{user_id}'
#     return await aredis.get(key)
