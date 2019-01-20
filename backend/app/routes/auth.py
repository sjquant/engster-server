from sanic.response import json
from sanic import Blueprint

from app.models import User

auth_bp = Blueprint('_auth_bp', url_prefix='/auth')


@auth_bp.route('/register', methods=['POST'])
async def register(request):
    """ register user """
    user = await User().create_user(**request.json)
    return json({'email': user.email})
