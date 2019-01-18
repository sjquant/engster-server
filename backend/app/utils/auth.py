from sanic_jwt import exceptions
from app.models import User


async def authenticate(request, *args, **kwargs):
    """ authenticate user """
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    if not username or not password:
        raise exceptions.AuthenticationFailed("Missing username or password.")

    user = await User.query.where(User.email == username).gino.first()

    if user is None:
        raise exceptions.AuthenticationFailed("User not found.")

    if not user.check_password(password):
        raise exceptions.AuthenticationFailed("Password is incorrect.")

    return user
