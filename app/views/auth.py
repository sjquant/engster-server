import asyncpg
from sanic import Blueprint
from sanic.request import Request
from sanic.exceptions import ServerError
from sanic_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
)
from sanic_jwt_extended.tokens import Token

from app.db_models import User
from app.utils.response import JsonResponse
from app.utils.validators import expect_body

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
        dict(access_token=access_token, refresh_token=refresh_token, **user.to_dict()),
        status=201,
    )


@blueprint.route("/obtain-token", methods=["POST"])
async def obtain_token(request: Request):
    username = request.json.get("email", None)
    password = request.json.get("password", None)

    user = await User.query.where(User.email == username).gino.first()

    if user is None:
        raise ServerError("User not found.", status_code=404)

    if not user.check_password(password):
        raise ServerError("Password is wrong.", status_code=400)

    access_token = await create_access_token(app=request.app, identity=str(user.id))
    refresh_token = await create_refresh_token(app=request.app, identity=str(user.id))

    return JsonResponse(
        dict(access_token=access_token, refresh_token=refresh_token, **user.to_dict()),
        status=201,
    )


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
    return JsonResponse(
        {"access_token": access_token, "refresh_token": refresh_token}, status=201
    )
