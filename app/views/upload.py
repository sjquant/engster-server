import datetime
from io import BytesIO
import uuid

from sanic.request import Request
from sanic.blueprints import Blueprint
from sanic.exceptions import ServerError
import pandas as pd
from PIL import Image

from app.db_models import Line, Content, Translation
from app.utils import JsonResponse, validate_file_size
from app.libs import converter


blueprint = Blueprint("upload_blueprint")


@blueprint.route("/create/csv", methods=["POST"])
async def create_csv(request):
    """
    Convert Single File

    Body Params
    ----------
    {
        "input": str,
        "output": str
    }
    """
    app = request.app
    input_text = request.files.get("input").body.decode(
        encoding="cp949", errors="ignore"
    )
    ext = request.files.get("input").name.split(".")[-1]
    output_name = request.form.get("output")

    lines = converter.read_lines(input_text, ext)
    df = converter.lines_to_df(lines)

    output_dir = app.config["CSV_DOWNLOAD_PATH"]
    output = output_dir + "/" + output_name

    converter.df_to_csv(df, output)
    return JsonResponse(
        {"message": "successfully convertd subtitle to csv"}, status=201
    )


@blueprint.route("/create/mixed-csv", methods=["POST"])
async def create_mixed_csv(request):
    """
    Convert Single File

    Body Params
    ----------
    {
        "input_eng_path": str,
        "input_kor_path": str,
        "output_path": str
    }
    """
    app = request.app

    input_eng_text = request.files.get("input_eng").body.decode(
        encoding="cp949", errors="ignore"
    )
    input_eng_ext = request.files.get("input_eng").name.split(".")[-1]
    input_kor_text = request.files.get("input_kor").body.decode(
        encoding="cp949", errors="ignore"
    )
    input_kor_ext = request.files.get("input_kor").name.split(".")[-1]
    output_name = request.form.get("output")

    lines_eng = converter.read_lines(input_eng_text, input_eng_ext)
    lines_kor = converter.read_lines(input_kor_text, input_kor_ext)
    df_eng = converter.lines_to_df(lines_eng)
    df_kor = converter.lines_to_df(lines_kor)
    df = converter.combine_eng_kor(df_eng, df_kor)

    output_dir = app.config["CSV_DOWNLOAD_PATH"]
    output = output_dir + "/" + output_name

    converter.df_to_csv(df, output)

    return JsonResponse(
        {"message": "successfully combined eng and kor and converted it to csv"},
        status=201,
    )


@blueprint.route("/upload/eng-subtitle/<content_id:int>", methods=["POST"])
async def upload_eng_subtitle(request, content_id):
    content = await Content.get(content_id)
    if content is None:
        raise ServerError("No Such Instance", status_code=404)
    input_file = request.files.get("input_file")
    df = pd.read_csv(BytesIO(input_file.body), encoding="cp949", header=0)
    df.loc[:, "content_id"] = content_id
    df.time = df.time.apply(lambda x: datetime.datetime.strptime(x, "%H:%M:%S").time())
    eng_line_list = [
        dict(time=each[0], line=each[1], content_id=each[2])
        for each in df[["time", "line", "content_id"]].values
    ]
    await Line.insert().gino.all(*eng_line_list)

    return JsonResponse({"message": "eng subtitle uploaded..."}, status=201)


@blueprint.route("/upload/kor-subtitle/<content_id:int>", methods=["POST"])
async def update_kor_subtitle(request, content_id):
    lines = await Line.query.where(content_id == content_id).order_by("id").gino.all()

    if lines is None:
        # lines are necessary
        raise ServerError("No Such Instance", status_code=404)

    input_file = request.files.get("input_file")
    df = pd.read_csv(BytesIO(input_file.body), encoding="cp949", header=0)

    if len(lines) != len(df):
        return JsonResponse(
            {"message": "line and translation length does not match."}, status=400
        )

    df.loc[:, "content_id"] = content_id
    df.loc[:, "line_id"] = [each.id for each in lines]
    kor_line_list = [
        dict(translation=each[0], line_id=each[1], content_id=each[2])
        for each in df[["translation", "line_id", "content_id"]].values
    ]

    # Insert Line Data
    await Translation.insert().gino.all(*kor_line_list)

    return JsonResponse({"message": "kor subtitle uploaded..."}, status=201)


@blueprint.route("/upload/photo", methods=["POST"])
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
