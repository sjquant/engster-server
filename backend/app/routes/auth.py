from sanic import Blueprint
from sanic.response import json

from app.models import User
from app.utils.serializers import json_serial

auth_bp = Blueprint('_auth_bp', url_prefix='/auth')


@auth_bp.route('/register', methods=['POST'])
async def register(request):
    """ register user """
    user = await User().create_user(**request.json)
    return json(user.to_dict(), default=json_serial)
