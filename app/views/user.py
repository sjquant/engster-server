from uuid import UUID

from sanic import Blueprint
from sanic.request import Request
from sanic.views import HTTPMethodView
from sanic.exceptions import ServerError
from sanic_jwt_extended.tokens import Token

from app.services import user as service
from app.schemas import UserModel
from app.exceptions import DataDoesNotExist
from app.core.sanic_jwt_extended import jwt_required
from app.utils import JsonResponse

blueprint = Blueprint("user_blueprint", url_prefix="/users")


class UserProfileView(HTTPMethodView):
    @jwt_required
    async def get(self, request, user_id: str, token: Token):
        if str(user_id) != token.identity:
            return JsonResponse({"message": "Permission Denied"}, status=403)

        user = await service.get_user_by_id(user_id)
        return JsonResponse(UserModel.from_orm(user), status=200)

    @jwt_required
    async def patch(self, request: Request, user_id: str, token: Token):
        if str(user_id) != token.identity:
            return JsonResponse({"message": "Permission Denied"}, status=403)

        data = {key: value for key, value in request.json.items()}
        user = await service.get_user_by_id(user_id)
        await user.update(**data).apply()
        return JsonResponse(UserModel.from_orm(user), status=200)

    async def delete(self):
        raise ServerError(status_code=405)


class UserActivitySummary(HTTPMethodView):
    async def get(self, request: Request, user_id: UUID):
        try:
            resp = await service.get_activitiy_summary(user_id)
        except DataDoesNotExist as e:
            return JsonResponse({"message": str(e)}, status=404)
        return JsonResponse(resp, status=200)


blueprint.add_route(UserProfileView.as_view(), "/<user_id:uuid>/profile")
blueprint.add_route(UserActivitySummary.as_view(), "/<user_id:uuid>/activity-summary")
