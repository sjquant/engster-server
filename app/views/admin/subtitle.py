from io import BytesIO
from typing import List
import datetime

from sanic.exceptions import ServerError
from sanic.blueprints import Blueprint

import pandas as pd

from app.core import converter
from app.utils.response import JsonResponse
from app.utils.validators import expect_body
from app.db_models import (
    Line,
    Content,
    ContentXGenre,
    Category,
    Genre,
    Translation,
)

blueprint = Blueprint('admin_subtitle_blueprint')


@blueprint.route('/convert_subtitle', methods=['POST'])
async def convert_single_file(request):
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
    input_text = request.files.get('input').body.decode(
        encoding='cp949', errors='ignore')
    ext = request.files.get('input').name.split('.')[-1]
    output_name = request.form.get('output')

    lines = converter.read_lines(input_text, ext)
    df = converter.lines_to_df(lines)

    output_dir = app.config['SETTINGS']['csv_download_dir']
    output = output_dir + '/' + output_name

    converter.df_to_csv(df, output)
    return JsonResponse({
        "message": "successfully convertd subtitle to csv"
    }, status=201)


@blueprint.route('/combine_convert', methods=['POST'])
async def combine_to_single_file(request):
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

    input_eng_text = request.files.get('input_eng').body.decode(
        encoding='cp949', errors='ignore')
    input_eng_ext = request.files.get('input_eng').name.split('.')[-1]
    input_kor_text = request.files.get('input_kor').body.decode(
        encoding='cp949', errors='ignore')
    input_kor_ext = request.files.get('input_kor').name.split('.')[-1]
    output_name = request.form.get('output')

    lines_eng = converter.read_lines(
        input_eng_text, input_eng_ext)
    lines_kor = converter.read_lines(
        input_kor_text, input_kor_ext)
    df_eng = converter.lines_to_df(lines_eng)
    df_kor = converter.lines_to_df(lines_kor)
    df = converter.combine_eng_kor(df_eng, df_kor)

    output_dir = app.config['SETTINGS']['csv_download_dir']
    output = output_dir + '/' + output_name

    converter.df_to_csv(df, output)

    return JsonResponse({
        "message": "successfully combined eng and kor and converted it to csv"
    }, status=201)


@blueprint.route('/upload_content', methods=['POST'])
@expect_body(
    title=(str, ...),
    year=(str, ...),
    reference=str,
    category_id=(int, ...),
    genre_ids=(List[int], ...)
)
async def upload_content(request):
    """
    Upload Single File
    """
    title = request.json['title']
    year = request.json['year']
    reference = request.json['reference']
    category_id = request.json['category_id']
    genre_ids = request.json['genre_ids']

    category = await Category.get(category_id)
    genres = await Genre.query.where(
        Genre.id.in_(genre_ids)).gino.all()
    content = Content(
        title=title,
        year=year,
        reference=reference,
        category_id=category.id
    )

    await content.create()

    content_genre_list = [
        dict(content_id=content.id, genre_id=genre.id) for genre in genres]

    await ContentXGenre.insert().gino.all(*content_genre_list)

    return JsonResponse(content.to_dict(), status=201)


@blueprint.route('/upload_eng_subtitle/<content_id:int>', methods=['POST'])
async def upload_eng_subtitle(request, content_id):
    content = await Content.get(content_id)
    if content is None:
        raise ServerError("No Such Instance", status_code=404)
    input_file = request.files.get('input_file')
    df = pd.read_csv(BytesIO(input_file.body),
                     encoding='cp949', header=0)
    df.loc[:, 'content_id'] = content_id
    df.time = df.time.apply(
        lambda x: datetime.datetime.strptime(x, '%H:%M:%S').time())
    eng_line_list = [dict(time=each[0], line=each[1], content_id=each[2])
                     for each in df[['time', 'line', 'content_id']].values]
    await Line.insert().gino.all(*eng_line_list)

    return JsonResponse({'message': 'eng subtitle uploaded...'}, status=201)


@blueprint.route('/upload_kor_subtitle/<content_id:int>', methods=['POST'])
async def update_kor_subtitle(request, content_id):
    lines = await Line.query.where(content_id == content_id).order_by('id').gino.all()

    if lines is None:
        # lines are necessary
        raise ServerError("No Such Instance", status_code=404)

    input_file = request.files.get('input_file')
    df = pd.read_csv(BytesIO(input_file.body),
                     encoding='cp949', header=0)

    if len(lines) != len(df):
        return JsonResponse({'message': 'line and translation length does not match.'}, status=400)

    df.loc[:, 'content_id'] = content_id
    df.loc[:, 'line_id'] = [each.id for each in lines]
    kor_line_list = [dict(translation=each[0], line_id=each[1], content_id=each[2])
                     for each in df[['translation', 'line_id', 'content_id']].values]

    # Insert Line Data
    await Translation.insert().gino.all(*kor_line_list)

    return JsonResponse({'message': 'kor subtitle uploaded...'}, status=201)
