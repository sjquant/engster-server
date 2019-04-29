import asyncpg
from sanic.request import Request
from sanic.blueprints import Blueprint
from sanic.views import HTTPMethodView
from sanic_jwt_extended.tokens import Token

from app import db
from app.models import LineLike
from app.utils.jwt import jwt_required

from app.utils.serializer import jsonify

blueprint = Blueprint('like_blueprint', url_prefix='/like')


class LikeEnglish(HTTPMethodView):

    async def get(self):
        return

    @jwt_required
    async def post(self, request: Request, line_id: int, token: Token):
        user_id = token.jwt_identity
        like = LineLike(line_id=line_id, user_id=user_id)
        try:
            await like.create()
        except asyncpg.exceptions.UniqueViolationError:
            return jsonify({'message': 'already liked'}, 400)
        return jsonify({'message': 'liked'}, 201)

    @jwt_required
    async def delete(self, request: Request, line_id: int, token: Token):
        user_id = token.jwt_identity
        await LineLike.delete.where(
            db.and_(
                LineLike.line_id == line_id,
                LineLike.user_id == user_id
            )
        ).gino.status()
        return jsonify({'message': 'deleted like'}, 204)


blueprint.add_route(LikeEnglish.as_view(), '/english/<line_id:int>')
