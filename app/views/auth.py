import asyncpg
from sanic import Blueprint
from sanic.request import Request
from sanic.exceptions import ServerError
from sanic_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    jwt_required,
)
from sanic_jwt_extended.tokens import Token

from app.db_models import User
from app.utils.response import JsonResponse
from app.utils.validators import expect_body
from app.models import AuthModel, UserModel
from app.utils.views import DetailAPIView

blueprint = Blueprint("auth_blueprint", url_prefix="/auth")


@blueprint.route("/register", methods=["POST"])
@expect_body(
    email=(str, ...), password=(str, ...), nickname=(str, None), is_admin=(bool, False)
)
async def register(request: Request):
    """ register user """

    try:
        user = await User().create_user(**request.json)
    except asyncpg.exceptions.UniqueViolationError:
        raise ServerError("Already Registered", status_code=400)

    access_token = await create_access_token(app=request.app, identity=str(user.id))
    refresh_token = await create_refresh_token(app=request.app, identity=str(user.id))

    return JsonResponse(
        AuthModel(
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

    user = await User.query.where(User.email == email).gino.first()

    if user is None:
        raise ServerError("User not found.", status_code=404)

    if not user.check_password(password):
        raise ServerError("Password is wrong.", status_code=400)

    access_token = await create_access_token(app=request.app, identity=str(user.id))
    refresh_token = await create_refresh_token(app=request.app, identity=str(user.id))

    return JsonResponse(
        AuthModel(
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
    user_id = token.jwt_identity

    user = await User.query.where(User.id == user_id).gino.first()

    if user is None:
        raise ServerError("User not found.", status_code=404)

    if user.check_password(original_password):
        user.set_password(new_password)
        await user.update(password_hash=user.password_hash).apply()
    else:
        raise ServerError("Password is wrong.", status_code=400)
    return JsonResponse({"message": "Password successfully updated"}, status=202)


@blueprint.route("/refresh-token", methods=["POST"])
@jwt_refresh_token_required
async def refresh_token(request, token: Token):
    """ refresh access token """
    access_token = await create_access_token(
        app=request.app, identity=token.jwt_identity
    )
    refresh_token = await create_refresh_token(
        app=request.app, identity=token.jwt_identity
    )

    user = await User.query.where(User.id == token.jwt_identity).gino.first()
    return JsonResponse(
        AuthModel(
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
        user_id = token.jwt_identity
        user = await super().get(request, id=user_id, return_obj=True)
        return JsonResponse(
            user.to_dict(show=["id", "email", "nickname", "photo"]), status=200
        )

    @jwt_required
    @expect_body(email=(str, None), nickname=(str, None), photo=(str, None))
    async def put(self, request: Request, token: Token):
        user_id = token.jwt_identity
        user = await super().put(request, id=user_id, return_obj=True)
        return JsonResponse(
            user.to_dict(show=["id", "email", "nickname", "photo"]), status=202
        )

    async def delete(self):
        raise ServerError(status_code=405)


blueprint.add_route(UserProfileView.as_view(), "/profile")
