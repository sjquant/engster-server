from sanic_jwt import exceptions, Responses
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


class CustomResponse(Responses):
    """
    Extend JWT Sanic Response
    """
    @staticmethod
    def extend_authenticate(request,
                            user=None,
                            access_token=None,
                            refresh_token=None):
        user_dict = user.to_dict()
        user_dict['id'] = str(user_dict['id'])

        return {
            'user': user_dict
        }

    # @staticmethod
    # def extend_retrieve_user(request, user=None, payload=None):
    #     return {}

    # @staticmethod
    # def extend_verify(request, user=None, payload=None):
    #     return {}

    # @staticmethod
    # def extend_refresh(request,
    #                    user=None,
    #                    access_token=None,
    #                    refresh_token=None,
    #                    purported_token=None,
    #                    payload=None):
    #     return {}

# async def store_refresh_token(user_id, refresh_token, *args, **kwargs):
#     key = f'refresh_token_{user_id}'
#     await aredis.set(key, refresh_token)


# async def retrieve_refresh_token(request, user_id, *args, **kwargs):
#     key = f'refresh_token_{user_id}'
#     return await aredis.get(key)
