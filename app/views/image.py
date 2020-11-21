from io import BytesIO
import uuid

from sanic.request import Request
from sanic.blueprints import Blueprint
from sanic.exceptions import ServerError
from sanic_jwt_extended import jwt_required
from sanic_jwt_extended.tokens import Token
from PIL import Image

from app.utils import JsonResponse, validate_file_size


blueprint = Blueprint("image_blueprint", url_prefix="images")


@blueprint.route("/upload", methods=["POST"])
@jwt_required
async def upload_photo(request: Request, token: Token):
    photo = request.files.get("photo")
    if not validate_file_size(photo, 1e7):
        raise ServerError(
            "Image too large, you can upload files up 10MB", status_code=413
        )
    extension = photo.type.split("/")[-1]
    path = f"media/photos/{str(uuid.uuid4())}.{extension}"
    image = Image.open(BytesIO(photo.body))
    image.save(path, extension)
    return JsonResponse({"path": f"{path}"}, status=201)
