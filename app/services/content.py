from typing import List, Dict, Any, Optional

from app import db
from app.models import Line, Content, Genre, ContentXGenre


async def fetch(limit: int, cursor: Optional[int] = None) -> List[Dict[str, Any]]:
    """Fetch contents"""

    query = db.select([Content.id, Content.title, Content.year, Content.poster])
    if cursor:
        query = (
            query.where(Content.id < cursor).limit(limit).order_by(Content.id.desc())
        )
    else:
        query = query.limit(limit).order_by(Content.id.desc())

    columns = ["id", "title", "year", "poster"]
    data = await query.gino.all()
    return [dict(zip(columns, each)) for each in data]


async def get_by_id(content_id: int) -> Content:
    content = await Content.query.where(Content.id == content_id).gino.first()
    return content


async def fetch_genres(content_ids: List[int]) -> Dict[str, Dict[str, Any]]:
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


async def add_genres(content: Content, genre_ids: List[int]) -> None:
    """Add genres to content"""
    content_x_genres = [
        dict(content_id=content.id, genre_id=genre_id) for genre_id in genre_ids
    ]
    if content_x_genres:
        await ContentXGenre.insert().gino.all(*content_x_genres)


async def clear_genres(content_id: int) -> None:
    """Clear genres of a content"""
    await ContentXGenre.delete.where(
        ContentXGenre.content_id == content_id
    ).gino.status()


async def fetch_subtitles(
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
