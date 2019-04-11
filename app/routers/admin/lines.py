import os
import datetime
from io import BytesIO
from typing import Optional

import pandas as pd
from sanic.exceptions import ServerError

from .blueprint import admin_bp
from app.core import converter
from app.utils.serializer import jsonify
from app import models, db


@admin_bp.route('/lines/convert_subtitle', methods=['POST'])
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
    return jsonify({
        "message": "successfully convertd subtitle to csv"
    }, 201)


@admin_bp.route('/lines/combine_convert', methods=['POST'])
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

    return jsonify({
        "message": "successfully combined eng and kor and converted it to csv"
    }, status=201)


@admin_bp.route('/lines/upload_content', methods=['POST'])
async def upload_content(request):
    """
    Upload Single File

    Body Params
    ----------
    {
        "title": str,
        "year": str,
        "reference": str,
        "category_id": int,
        "genre_ids": array
    }
    """
    title = request.json['title']
    year = request.json['year']
    reference = request.json['reference']
    category_id = request.json['category_id']
    genre_ids = request.json['genre_ids']

    category = await models.Category.get(category_id)
    genres = await models.Genre.query.where(
        models.Genre.id.in_(genre_ids)).gino.all()
    content = models.Content(
        title=title,
        year=year,
        reference=reference,
        category_id=category.id
    )

    await content.create()

    content_genre_list = [
        dict(content_id=content.id, genre_id=genre.id) for genre in genres]

    await models.ContentXGenre.insert().gino.all(*content_genre_list)

    return jsonify(content.to_dict(), 201)


@admin_bp.route('/lines/upload_eng_subtitle/<content_id:int>', methods=['POST'])
async def upload_eng_subtitle(request, content_id):
    content = await models.Content.get(content_id)
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
    await models.Line.insert().gino.all(*eng_line_list)

    return jsonify({'message': 'eng subtitle uploaded...'}, 201)


@admin_bp.route('/lines/upload_kor_subtitle/<content_id:int>', methods=['POST'])
async def update_kor_subtitle(request, content_id):
    lines = await models.Line.query.where(content_id == content_id).gino.all()

    if lines is None:
        # lines are necessary
        raise ServerError("No Such Instance", status_code=404)

    input_file = request.files.get('input_file')
    df = pd.read_csv(BytesIO(input_file.body),
                     encoding='cp949', header=0)

    if len(lines) != len(df):
        return jsonify({'message': 'line and translation length does not match.'}, 400)

    df.loc[:, 'content_id'] = content_id
    df.loc[:, 'line_id'] = [each.id for each in lines]
    kor_line_list = [dict(translation=each[0], line_id=each[1], content_id=each[2])
                     for each in df[['translation', 'line_id', 'content_id']].values]

    # Insert Line Data
    await models.Translation.insert().gino.all(*kor_line_list)

    return jsonify({'message': 'kor subtitle uploaded...'}, 201)