from typing import List, Dict, Any, Optional
from uuid import UUID

from app import db
from app.db_models import (
    User,
    Line,
    Translation,
    Content,
    Genre,
    Category,
    ContentXGenre,
    TranslationLike,
    LineLike,
)


async def fetch_contents(
    limit: int, cursor: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Fetch contents"""

    query = db.select(
        [
            Content.id,
            Content.title,
            Content.year,
            Content.poster,
            Category.id,
            Category.category,
        ]
    ).select_from(Content.join(Category, Content.category_id == Category.id))
    if cursor:
        query = (
            query.where(Content.id < cursor).limit(limit).order_by(Content.id.desc())
        )
    else:
        query = query.limit(limit).order_by(Content.id.desc())

    columns = ["id", "title", "year", "poster", "category_id", "category_name"]
    data = await query.gino.all()
    return [dict(zip(columns, each)) for each in data]


async def get_content_by_id(content_id: int) -> Content:
    content = await Content.query.where(Content.id == content_id).gino.first()
    return content


async def fetch_all_categories() -> List[Dict[str, Any]]:
    """Fetch all categories"""
    data = await Category.query.gino.all()
    return [each.to_dict() for each in data]


async def get_category_by_id(category_id: int) -> Category:
    category = await Category.query.where(Category.id == category_id).gino.first()
    return category


async def fetch_all_genres() -> List[Dict[str, Any]]:
    """Fetch all genres"""
    data = await Genre.query.gino.all()
    return [each.to_dict() for each in data]


async def fetch_genres_by_ids(genre_ids) -> List[Dict[str, Any]]:
    """Fetch genres by ids"""
    data = await Genre.query.where(Genre.id.in_(genre_ids)).gino.all()
    return [each.to_dict() for each in data]


async def get_genre_by_id(genre_id: int) -> Genre:
    genre = await Genre.query.where(Genre.id == genre_id).gino.first()
    return genre


async def add_genres_to_content(content: Content, genres: List[Dict[str, Any]]) -> None:
    """Add genres to content"""
    content_x_genres = [
        dict(content_id=content.id, genre_id=genre["id"]) for genre in genres
    ]
    await ContentXGenre.insert().gino.all(*content_x_genres)


async def empty_content_of_gneres(content_id: int) -> None:
    await ContentXGenre.delete.where(
        ContentXGenre.content_id == content_id
    ).gino.status()


async def fetch_content_lines(
    content_id: int, limit: int = 20, cursor: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Fetch lines of a content"""
    condition = (
        db.and_(Line.id < cursor, Line.content_id == content_id)
        if cursor
        else Line.content_id == content_id
    )

    query = Line.query.where(condition).order_by(Line.id.desc()).limit(limit)
    data = await query.gino.all()
    return [each.to_dict() for each in data]


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


async def fetch_user_liked_english_lines(
    user_id: UUID, line_ids: List[int]
) -> List[int]:
    query = db.select([LineLike.line_id]).where(
        db.and_(LineLike.user_id == user_id, LineLike.line_id.in_(line_ids))
    )
    data = await query.gino.all()
    return [each[0] for each in data]


async def fetch_user_liked_korean_lines(
    user_id: UUID, translation_ids: List[int]
) -> List[int]:
    query = db.select([TranslationLike.translation_id]).where(
        db.and_(
            TranslationLike.user_id == user_id,
            TranslationLike.translation_id.in_(translation_ids),
        )
    )
    data = await query.gino.all()
    return [each[0] for each in data]


async def search_english_lines(
    keyword: str, limit: int = 20, cursor: Optional[int] = None
):
    """Search English with a keyword"""
    condition = (
        db.and_(Line.id < cursor, Line.line.op("~*")(keyword))
        if cursor
        else Line.line.op("~*")(keyword)
    )
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
        .where(condition)
        .select_from(
            Line.join(Content, Line.content_id == Content.id).join(
                Category, Content.category_id == Category.id
            )
        )
        .limit(limit)
        .order_by(Line.id.desc())
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


async def count_english_lines(keyword: str) -> int:
    query = db.select([db.func.count(Line.id)]).where(Line.line.op("~*")(keyword))
    return await query.gino.scalar()


async def count_korean_lines(keyword: str) -> int:
    query = db.select([db.func.count(Translation.id)]).where(
        Translation.translation.op("~*")(keyword)
    )
    return await query.gino.scalar()


async def randomly_pick_subtitles(count=30) -> List[Optional[Dict[str, Any]]]:
    total_count = await db.select([db.func.count(Line.id)]).gino.scalar()
    if total_count == 0:
        return []

    percentage = count / total_count
    query = (
        db.select(
            [
                db.func.distinct(Line.id),
                Line.line,
                Translation.id,
                Translation.translation,
                Content.id,
                Content.title,
                Content.year,
                Category.id,
                Category.category,
            ]
        )
        .select_from(
            Line.join(Content, Line.content_id == Content.id)
            .join(Translation, Line.id == Translation.line_id)
            .join(Category, Content.category_id == Category.id)
        )
        .where(db.func.random() < percentage)
    )
    columns = (
        "id",
        "line",
        "translation_id",
        "translation",
        "content_id",
        "content_title",
        "content_year",
        "category_id",
        "category_name",
    )
    data = await query.gino.all()
    return [dict(zip(columns, each)) for each in data]


async def search_korean_lines(
    keyword: str, limit: int = 20, cursor: Optional[int] = None
):
    """Search Korean with a keyword"""
    condition = (
        db.and_(Translation.id < cursor, Translation.translation.op("~*")(keyword))
        if cursor
        else Translation.translation.op("~*")(keyword)
    )
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
        .where(condition)
        .select_from(
            Translation.join(Line, Translation.line_id == Line.id)
            .join(Content, Line.content_id == Content.id)
            .join(Category, Content.category_id == Category.id)
        )
        .limit(limit)
        .order_by(Translation.id.desc())
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


async def fetch_genres_per_content(content_ids: List[int]) -> Dict[str, Dict[str, Any]]:
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


async def fetch_translations(
    line_id: int, limit: int = 15, cursor: Optional[int] = None
) -> List[Dict[str, Any]]:
    condition = (
        db.and_(Translation.id < cursor, Translation.line_id == line_id)
        if cursor
        else Translation.line_id == line_id
    )
    query = (
        Translation.load(user=User.on(Translation.user_id == User.id))
        .query.where(condition)
        .limit(limit)
    )
    data = await query.gino.all()
    translations = []
    for each in data:
        try:
            user = each.user.to_dict(show=["id", "nickname"])
        except AttributeError:
            user = {"id": None, "nickname": "자막"}
        translations.append({**each.to_dict(hide=["user_id"]), "user": user})
    return translations


async def get_translation_by_id(translation_id: int) -> Translation:
    query = Translation.query.where(db.and_(Translation.id == translation_id))
    translation = query.gino.first()
    return translation


async def create_english_like(line_id: int, user_id: UUID) -> LineLike:
    like = LineLike(line_id=line_id, user_id=user_id)
    await like.create()
    return like


async def delete_english_like(line_id: int, user_id: UUID) -> None:
    await LineLike.delete.where(
        db.and_(LineLike.line_id == line_id, LineLike.user_id == user_id)
    ).gino.status()


async def create_korean_like(translation_id: int, user_id: UUID) -> LineLike:
    like = TranslationLike(translation_id=translation_id, user_id=user_id)
    await like.create()
    return like


async def delete_korean_like(translation_id: int, user_id: UUID) -> None:
    await TranslationLike.delete.where(
        db.and_(
            TranslationLike.translation_id == translation_id,
            TranslationLike.user_id == user_id,
        )
    ).gino.status()
