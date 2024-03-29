import datetime

from sanic import Blueprint
from sanic.request import Request
from sanic_jwt_extended import jwt_required, refresh_jwt_required, jwt_optional
from sanic_jwt_extended.tokens import Token
import asyncpg

from app import JWT
from app.core.sanic_jwt_extended import (
    set_access_cookie,
    set_refresh_cookie,
    remove_access_cookie,
    remove_refresh_cookie,
)
from app.core.email import send_password_reset_email
from app.core.jwt import encode_jwt, decode_jwt
from app.services.user import get_user_by_email, get_user_by_id, create_user
from app.utils import JsonResponse
from app.decorators import expect_body
from app.schemas import UserModel
from app.vendors.sanic_oauth import GoogleClient, FacebookClient, NaverClient

blueprint = Blueprint("auth_blueprint", url_prefix="/auth")


@blueprint.route("/register", methods=["POST"])
@expect_body(email=(str, ...), password=(str, ...), nickname=(str, None))
async def register(request: Request):
    """register user"""

    try:
        user = await create_user(**request.json, is_admin=False)
    except asyncpg.exceptions.UniqueViolationError:
        return JsonResponse({"message": "User already exists"}, status=400)

    access_token = JWT.create_access_token(identity=str(user.id), role="user")
    refresh_token = JWT.create_refresh_token(identity=str(user.id))
    resp = JsonResponse({"new": True, "user": UserModel.from_orm(user)}, status=201)
    set_access_cookie(resp, access_token)
    set_refresh_cookie(resp, refresh_token)
    return resp


@blueprint.route("/obtain-token", methods=["POST"])
async def obtain_token(request: Request):
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    user = await get_user_by_email(email)
    if user is None:
        return JsonResponse({"message": "User not found."}, status=404)
    try:
        if not user.check_password(password):
            return JsonResponse({"message": "Wrong password"}, status=400)
    except ValueError:
        return JsonResponse({"message": "Wrong password"}, status=400)

    role = "admin" if user.is_admin else "user"
    access_token = JWT.create_access_token(identity=str(user.id), role=role)
    refresh_token = JWT.create_refresh_token(identity=str(user.id))
    resp = JsonResponse(
        {"new": False, "user": UserModel.from_orm(user), "token": access_token},
        status=201,
    )
    set_access_cookie(resp, access_token)
    set_refresh_cookie(resp, refresh_token)
    return resp


@blueprint.route("/sign-out", methods=["POST"])
async def sign_out(request: Request):

    resp = JsonResponse({"message": "success"}, status=200)
    remove_access_cookie(resp)
    remove_refresh_cookie(resp)
    return resp


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
        return JsonResponse({"message": "Unknown Provider"}, status=400)
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

    role = "admin" if user.is_admin else "user"
    access_token = JWT.create_access_token(identity=str(user.id), role=role)
    refresh_token = JWT.create_refresh_token(identity=str(user.id))
    resp = JsonResponse(
        {"new": is_new, "user": UserModel.from_orm(user), "token": access_token},
        status=201,
    )
    set_access_cookie(resp, access_token)
    set_refresh_cookie(resp, refresh_token)
    return resp


@blueprint.route("/reset-password", methods=["PUT"])
@jwt_required
@expect_body(original_password=(str, ...), new_password=(str, ...))
async def reset_password(request: Request, token: Token):
    original_password = request.json.get("original_password")
    new_password = request.json.get("new_password")
    user_id = token.identity

    user = await get_user_by_id(user_id)

    if user is None:
        return JsonResponse({"message": "User not found"}, status=404)

    try:
        validated = user.check_password(original_password)
    except ValueError:
        return JsonResponse({"message": "Wrong password"}, status=400)
    if validated:
        user.set_password(new_password)
        await user.update(password_hash=user.password_hash).apply()
    else:
        return JsonResponse({"message": "Wrong password"}, status=400)
    return JsonResponse({"message": "Password successfully updated"}, status=200)


@blueprint.route("/refresh-token", methods=["POST"])
@refresh_jwt_required
async def refresh_token(request, token: Token):
    """refresh access token"""
    access_token = JWT.create_access_token(identity=token.identity, role=token.role)
    user_id = token.identity
    user = await get_user_by_id(user_id)
    resp = JsonResponse({"new": False, "user": UserModel.from_orm(user)}, status=201)
    set_access_cookie(resp, access_token)
    return resp


@blueprint.route("/validate-token", methods=["POST"])
@jwt_optional
async def validate_token(request, token: Token):
    """Inspect token and"""
    if not token:
        return JsonResponse({"message": "No token"}, status=404)

    user_id = token.identity
    user = await get_user_by_id(user_id)
    resp = JsonResponse(
        {
            "expired_at": int(token.exp.timestamp() * 1000),
            "user": UserModel.from_orm(user),
        },
        status=200,
    )
    return resp


@blueprint.route("/reset-lost-password/request", methods=["POST"])
async def request_password_reset(request):
    """Request password reset by email"""
    email = request.json.get("email")
    user = await get_user_by_email(email)
    if user is None:
        return JsonResponse({"message": "User not found"}, status=404)
    token = encode_jwt(
        {"user_id": str(user.id)}, expires_delta=datetime.timedelta(minutes=30)
    )
    reset_password_link = f"https://engster.co.kr/reset-lost-password?t={token}"
    await send_password_reset_email(email, reset_password_link)
    return JsonResponse({"message": "success"}, status=200)


@blueprint.route("/reset-lost-password", methods=["POST"])
async def reset_lost_password(request):
    """Request password reset by email"""
    password = request.json.get("password")
    token = request.json.get("token")

    data = decode_jwt(token)
    user_id = data["user_id"]
    user = await get_user_by_id(user_id)
    user.set_password(password)
    await user.update(password_hash=user.password_hash).apply()

    return JsonResponse({"message": "success"}, status=200)
