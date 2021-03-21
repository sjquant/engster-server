from typing import Optional, List

from sanic.views import HTTPMethodView
from sanic.blueprints import Blueprint
from sanic.request import Request
from sanic_jwt_extended.tokens import Token

from app.decorators import expect_query
from app.core.sanic_jwt_extended import admin_required

from app.services import translation_review as translation_review_service
from app.schemas import TranslationReviewStatus
from app.utils import JsonResponse

blueprint = Blueprint("translation_review_blueprint", url_prefix="translation-reviews")


class TranslationReviewListView(HTTPMethodView):
    @admin_required
    @expect_query(
        limit=(int, 20),
        cursor=(int, None),
        status=(List[TranslationReviewStatus], None),
    )
    async def get(
        self,
        request: Request,
        status: Optional[List[str]],
        limit: int,
        cursor: Optional[int],
        token: Token,
    ):
        data = await translation_review_service.fetch(status, limit, cursor)
        return JsonResponse({"data": data, "cursor": cursor, "limit": limit})


blueprint.add_route(TranslationReviewListView.as_view(), "")
