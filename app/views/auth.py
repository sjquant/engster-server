import asyncpg
from sanic import Blueprint
from sanic.request import Request
from sanic.exceptions import ServerError
from sanic_jwt_extended import (
    refresh_jwt_required,
    jwt_required,
)
from sanic_jwt_extended.tokens import Token

from app import JWT
from app.db_models import User
from app.db_access.user import get_user_by_email, get_user_by_id, create_user
from app.utils import JsonResponse
from app.decorators import expect_body
from app.models import AuthModel, UserModel
from app.libs.views import DetailAPIView
from app.vendors.sanic_oauth import GoogleClient, FacebookClient, NaverClient

blueprint = Blueprint("auth_blueprint", url_prefix="/auth")


@blueprint.route("/register", methods=["POST"])
@expect_body(
    email=(str, ...), password=(str, ...), nickname=(str, None), is_admin=(bool, False)
)
async def register(request: Request):
    """ register user """

    try:
        user = await create_user(**request.json)
    except asyncpg.exceptions.UniqueViolationError:
        raise ServerError("Already Registered", status_code=400)

    access_token = JWT.create_access_token(identity=str(user.id))
    refresh_token = JWT.create_refresh_token(identity=str(user.id))

    return JsonResponse(
        AuthModel(
            is_new=True,
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserModel.from_orm(user),
        ),
        status=201,
    )


@blueprint.route("/obtain-token", methods=["POST"])
async def obtain_token(request: Request):
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    user = await get_user_by_email(email)

    if user is None:
        raise ServerError("User not found.", status_code=404)

    if not user.check_password(password):
        raise ServerError("Password is wrong.", status_code=400)

    access_token = JWT.create_access_token(identity=str(user.id))
    refresh_token = JWT.create_refresh_token(identity=str(user.id))

    return JsonResponse(
        AuthModel(
            is_new=False,
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserModel.from_orm(user),
        ),
        status=201,
    )


def get_client(request, provider: str):
    app = request.app
    if provider == "google":
        client = GoogleClient(
            request.app.async_session,
            client_id=app.config["GOOGLE_CLIENT_ID"],
            client_secret=app.config["GOOGLE_CLIENT_SECRET"],
        )
    elif provider == "facebook":
        client = FacebookClient(
            request.app.async_session,
            client_id=app.config["FB_CLIENT_ID"],
            client_secret=app.config["FB_CLIENT_SECRET"],
        )
    elif provider == "naver":
        client = NaverClient(
            request.app.async_session,
            client_id=app.config["NAVER_CLIENT_ID"],
            client_secret=app.config["NAVER_CLIENT_SECRET"],
        )
    else:
        raise ServerError("Unknown Provider", status_code=400)
    return client


@blueprint.route("/obtain-token/<provider:string>", methods=["POST"])
async def oauth_obtain_token(request: Request, provider: str):
    client = get_client(request, provider)
    await client.get_access_token(
        request.json.get("code"), redirect_uri=request.json.get("redirectUri")
    )
    user_info, _ = await client.user_info()
    user = await get_user_by_email(user_info.email)
    if user is None:
        user = await create_user(email=user_info.email, photo=user_info.picture)
        is_new = True
    else:
        is_new = False
    access_token = JWT.create_access_token(identity=str(user.id))
    refresh_token = JWT.create_refresh_token(identity=str(user.id))

    return JsonResponse(
        AuthModel(
            is_new=is_new,
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserModel.from_orm(user),
        ),
        status=201,
    )


@blueprint.route("/reset-password", methods=["PUT"])
@jwt_required
@expect_body(original_password=(str, ...), new_password=(str, ...))
async def reset_password(request: Request, token: Token):
    original_password = request.json.get("original_password")
    new_password = request.json.get("new_password")
    user_id = token.identity

    user = await get_user_by_id(user_id)

    if user is None:
        raise ServerError("User not found.", status_code=404)

    if user.check_password(original_password):
        user.set_password(new_password)
        await user.update(password_hash=user.password_hash).apply()
    else:
        raise ServerError("Password is wrong.", status_code=400)
    return JsonResponse({"message": "Password successfully updated"}, status=202)


@blueprint.route("/refresh-token", methods=["POST"])
@refresh_jwt_required
async def refresh_token(request, token: Token):
    """ refresh access token """
    access_token = JWT.create_access_token(identity=token.identity)
    refresh_token = JWT.create_refresh_token(identity=token.identity)
    user_id = token.identity

    user = await get_user_by_id(user_id)
    return JsonResponse(
        AuthModel(
            is_new=False,
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserModel.from_orm(user),
        ),
        status=201,
    )


class UserProfileView(DetailAPIView):
    model = User

    @jwt_required
    async def get(self, request, token: Token):
        user_id = token.identity
        user = await super().get(request, id=user_id, return_obj=True)
        return JsonResponse(UserModel.from_orm(user), status=200)

    @jwt_required
    @expect_body(email=(str, None), nickname=(str, None), photo=(str, None))
    async def put(self, request: Request, token: Token):
        user_id = token.identity
        user = await super().put(request, id=user_id, return_obj=True)
        return JsonResponse(UserModel.from_orm(user), status=202)

    async def delete(self):
        raise ServerError(status_code=405)


blueprint.add_route(UserProfileView.as_view(), "/profile")
