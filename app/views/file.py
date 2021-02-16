import mimetypes
import uuid

from sanic.request import Request
from sanic.blueprints import Blueprint
from sanic_jwt_extended import jwt_required
from sanic_jwt_extended.tokens import Token

import aiobotocore

from app.utils import JsonResponse
from app.config import AWS_SECRET_ACCESS_KEY, AWS_ACCESS_KEY_ID, AWS_BUCKET_NAME


blueprint = Blueprint("file", url_prefix="/file")


async def _generate_presigned_url(image_path: str):
    session = aiobotocore.get_session()
    async with session.create_client(
        "s3",
        region_name="ap-northeast-2",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    ) as client:
        content_type, _ = mimetypes.guess_type(image_path)

        if content_type is None:
            raise Exception("Failed to parse content type from filename")

        url = await client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": AWS_BUCKET_NAME,
                "Key": image_path,
                "ContentType": content_type,
            },
            ExpiresIn=300,  # 5 minutes
        )
    return url


@blueprint.route("/<file_type:string>/create-signed-url", methods=["POST"])
@jwt_required
async def create_sigined_url(request: Request, file_type: str, token: Token):
    app = request.json.get("app")
    filename = request.json.get("filename")
    ext = filename.split(".")[-1]
    new_filename = uuid.uuid4().hex + "." + ext
    image_path = f"{file_type}/{app}/{new_filename}"
    signed_url = await _generate_presigned_url(image_path)
    return JsonResponse(
        {"image_path": f"{image_path}", "signed_url": signed_url}, status=201
    )
