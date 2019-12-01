import base64
import uuid
from PIL import Image
from io import BytesIO

from sanic.request import Request
from sanic.blueprints import Blueprint

from app.utils.response import JsonResponse


blueprint = Blueprint("upload_blueprint", url_prefix="/upload")


@blueprint.route("/upload-photo", methods=["POST"])
async def upload_photo(request: Request):
    photo = request.json.get("photo")
    fmt, imgstr = photo.split(";base64")
    extension = fmt.split("/")[-1]
    image = base64.b64decode(imgstr)
    path = f"./{str(uuid.uuid4())}.{extension}"
    image = Image.open(BytesIO(image))
    image.save(path, extension)
    return JsonResponse({"photo_path": path})
