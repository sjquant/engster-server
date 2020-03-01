from typing import List, Dict, Any
from app import db
from app.db_models import (
    Line,
    Translation,
    Content,
    Genre,
    Category,
    ContentXGenre,
    TranslationLike,
    LineLike,
)


async def get_like_count_per_english_line(line_ids: List[int]) -> Dict[int, int]:
    """get like count per english_line"""
    query = (
        db.select([LineLike.line_id, db.func.count(LineLike.line_id)])
        .where(LineLike.line_id.in_(line_ids))
        .group_by(LineLike.line_id)
    )

    data = await query.gino.all()
    return {each[0]: each[1] for each in data}


async def get_like_count_per_korean_line(translation_ids: List[int]) -> Dict[int, int]:
    """get korean count per korean_line """
    query = (
        db.select(
            [
                TranslationLike.translation_id,
                db.func.count(TranslationLike.translation_id),
            ]
        )
        .where(TranslationLike.translation_id.in_(translation_ids))
        .group_by(TranslationLike.translation_id)
    )
    data = await query.gino.all()
    return {each[0]: each[1] for each in data}


async def get_user_liked_english_lines(user_id, line_ids: List[int]) -> List[int]:
    query = db.select([LineLike.line_id]).where(
        db.and_(LineLike.user_id == user_id, LineLike.line_id.in_(line_ids))
    )
    data = await query.gino.all()
    return [each[0] for each in data]


async def get_user_liked_korean_lines(user_id, translation_ids: List[int]) -> List[int]:
    query = db.select([TranslationLike.translation_id]).where(
        db.and_(
            TranslationLike.user_id == user_id,
            TranslationLike.translation_id.in_(translation_ids),
        )
    )
    data = await query.gino.all()
    return [each[0] for each in data]


async def search_english_lines(keyword, limit=15, offset=0):
    """Search English with a keyword"""
    query = (
        db.select(
            [
                Line.id,
                Line.line,
                Content.id,
                Content.title,
                Content.year,
                Category.id,
                Category.category,
            ]
        )
        .where(Line.line.op("~*")(keyword + r"[\.?, ]"),)
        .select_from(
            Line.join(Content, Line.content_id == Content.id).join(
                Category, Content.category_id == Category.id
            )
        )
        .limit(limit)
        .offset(offset)
    )
    columns = (
        "id",
        "line",
        "content_id",
        "content_title",
        "content_year",
        "category_id",
        "category_name",
    )
    data = await query.gino.all()
    return [dict(zip(columns, each)) for each in data]


async def search_korean_lines(keyword, limit=15, offset=0):
    """Search Koreanm with a keyword"""
    query = (
        db.select(
            [
                Translation.id,
                Translation.translation,
                Line.id,
                Line.line,
                Content.id,
                Content.title,
                Content.year,
                Category.id,
                Category.category,
            ]
        )
        .where(db.and_(Translation.translation.op("~*")(keyword + r"[\.?, ]"),))
        .select_from(
            Translation.join(Line, Translation.line_id == Line.id)
            .join(Content, Line.content_id == Content.id)
            .join(Category, Content.category_id == Category.id)
        )
        .limit(limit)
        .offset(offset)
    )
    columns = (
        "id",
        "translation",
        "line_id",
        "line",
        "content_id",
        "content_title",
        "content_year",
        "category_id",
        "category_name",
    )
    data = await query.gino.all()
    return [dict(zip(columns, each)) for each in data]


async def get_translation_count_per_line(line_ids: List[int]) -> Dict[int, int]:
    query = (
        db.select([Translation.line_id, db.func.count(Translation.line_id)])
        .where(Translation.line_id.in_(line_ids))
        .group_by(Translation.line_id)
    )
    data = await query.gino.all()
    translation_count_per_line = {each[0]: each[1] for each in data}
    return translation_count_per_line


async def get_genres_per_content(content_ids: List[int]) -> Dict[str, Dict[str, Any]]:
    """get genres of each content"""
    query = (
        db.select([Genre.id, Genre.genre, ContentXGenre.content_id])
        .select_from(Genre.join(ContentXGenre))
        .where(ContentXGenre.content_id.in_(content_ids))
    )
    data = await query.gino.all()
    genres: dict = {}
    for each in data:
        content = genres.setdefault(each[2], [])
        content.append({"id": each[0], "name": each[1]})
    return genres
