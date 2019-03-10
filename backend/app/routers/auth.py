import asyncpg
from sanic import Blueprint
from sanic.response import json
from sanic.exceptions import ServerError

from app.models import User
from app.utils.serializer import jsonify

auth_bp = Blueprint('_auth_bp', url_prefix='/auth')


@auth_bp.route('/register', methods=['POST'])
async def register(request):
    """ register user """

    try:
        user = await User().create_user(**request.json)
    except asyncpg.exceptions.UniqueViolationError:
        raise ServerError("Already Registered", status_code=400)
    return jsonify(user.to_dict())
