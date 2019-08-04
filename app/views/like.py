import asyncpg
from sanic.request import Request
from sanic.blueprints import Blueprint
from sanic_jwt_extended.tokens import Token
from sanic_jwt_extended import jwt_required

from app import db
from app.db_models import LineLike, TranslationLike
from app.utils.views import APIView
from app.utils.response import JsonResponse

blueprint = Blueprint("like_blueprint", url_prefix="/like")


class LikeEnglish(APIView):
    async def get(self, request: Request, line_id: int):
        likes = await LineLike.query.where(LineLike.line_id == line_id).gino.all()
        resp = [each.to_dict() for each in likes]

        return JsonResponse(resp, status=200)

    @jwt_required
    async def post(self, request: Request, line_id: int, token: Token):
        user_id = token.jwt_identity
        like = LineLike(line_id=line_id, user_id=user_id)
        try:
            await like.create()
        except asyncpg.exceptions.UniqueViolationError:
            return JsonResponse({"message": "already liked"}, status=400)
        return JsonResponse({"message": "liked"}, status=201)

    @jwt_required
    async def delete(self, request: Request, line_id: int, token: Token):
        user_id = token.jwt_identity
        await LineLike.delete.where(
            db.and_(LineLike.line_id == line_id, LineLike.user_id == user_id)
        ).gino.status()
        return JsonResponse({"message": "deleted like"}, status=204)


class LikeKorean(APIView):
    async def get(self, request: Request, translation_id: int):
        likes = await TranslationLike.query.where(
            TranslationLike.translation_id == translation_id
        ).gino.all()
        resp = [each.to_dict() for each in likes]

        return JsonResponse(resp, status=200)

    @jwt_required
    async def post(self, request: Request, translation_id: int, token: Token):
        user_id = token.jwt_identity
        like = TranslationLike(translation_id=translation_id, user_id=user_id)
        try:
            await like.create()
        except asyncpg.exceptions.UniqueViolationError:
            return JsonResponse({"message": "already liked"}, status=400)
        return JsonResponse({"message": "liked"}, status=201)

    @jwt_required
    async def delete(self, request: Request, translation_id: int, token: Token):
        user_id = token.jwt_identity
        await TranslationLike.delete.where(
            db.and_(
                TranslationLike.translation_id == translation_id,
                TranslationLike.user_id == user_id,
            )
        ).gino.status()
        return JsonResponse({"message": "deleted like"}, status=204)


blueprint.add_route(LikeEnglish.as_view(), "/english/<line_id:int>")
blueprint.add_route(LikeKorean.as_view(), "/korean/<translation_id:int>")
