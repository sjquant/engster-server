from sanic import Blueprint
from sanic.response import json

index_bp = Blueprint('_index_bp')


@index_bp.route('/', methods=['GET'])
async def home(request):
    return json({"Hello": "Engster"})
