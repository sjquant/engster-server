from io import BytesIO
import uuid

from sanic.request import Request
from sanic.blueprints import Blueprint
from sanic.exceptions import ServerError
from PIL import Image

from app.utils import JsonResponse, validate_file_size

blueprint = Blueprint("upload_blueprint", url_prefix="/upload")


@blueprint.route("/upload-photo", methods=["POST"])
async def upload_photo(request: Request):
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
