from typing import List, Dict, Any, Optional
from uuid import UUID

from app import db
from app.models import (
    User,
    Line,
    Translation,
    Content,
    LineLike,
)
from app.utils import fetch_all


async def search(keyword: str, limit: int = 20, cursor: Optional[int] = None):
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
                Content.id.label("content_id"),
                Content.title.label("content_title"),
                Content.year.label("content_year"),
            ]
        )
        .where(condition)
        .select_from(Line.join(Content, Line.content_id == Content.id))
        .limit(limit)
        .order_by(Line.id.desc())
    )

    data = await fetch_all(query)
    return data


async def count(keyword: str) -> int:
    """Count subtitles"""
    query = db.select([db.func.count(Line.id)]).where(Line.line.op("~*")(keyword))
    return await query.gino.scalar()


async def pick_randomly(max_count=30) -> List[Optional[Dict[str, Any]]]:
    total_count = await db.select([db.func.count(Line.id)]).gino.scalar()
    if total_count == 0:
        return []

    percentage = max_count / total_count
    query = (
        db.select(
            [
                db.func.distinct(Line.id).label("id"),
                Line.line,
                Translation.id.label("translation_id"),
                Translation.translation.label("translation"),
                Content.id.label("content_id"),
                Content.title.label("content_title"),
                Content.year.label("content_year"),
            ]
        )
        .select_from(
            Line.join(Content, Line.content_id == Content.id).join(
                Translation, Line.id == Translation.line_id
            )
        )
        .where(db.func.random() < percentage)
    )

    data = await fetch_all(query)
    return data


async def add_like(line_id: int, user_id: UUID) -> LineLike:
    like = LineLike(line_id=line_id, user_id=user_id)
    await like.create()
    return like


async def remove_like(line_id: int, user_id: UUID) -> None:
    await LineLike.delete.where(
        db.and_(LineLike.line_id == line_id, LineLike.user_id == user_id)
    ).gino.status()


async def fetch_user_liked(
    user_id: UUID, limit: int = 20, cursor: Optional[int] = 0
) -> List[Dict["str", Any]]:
    condition = (
        db.and_(LineLike.id < cursor, LineLike.user_id == user_id)
        if cursor
        else LineLike.user_id == user_id
    )
    query = (
        db.select(
            [
                Line.id,
                Line.line,
                Content.id.label("content_id"),
                Content.title.label("content_title"),
                Content.year.label("content_year"),
                LineLike.created_at,
            ]
        )
        .where(condition)
        .select_from(
            Line.join(Content, Line.content_id == Content.id).join(
                LineLike, Line.id == LineLike.line_id
            )
        )
        .limit(limit)
        .order_by(LineLike.id.desc())
    )

    data = await fetch_all(query)
    return data


async def fetch_translation_count(line_ids: List[int]) -> Dict[int, int]:
    """Get translation_count"""
    query = (
        db.select([Translation.line_id, db.func.count(Translation.line_id)])
        .where(Translation.line_id.in_(line_ids))
        .group_by(Translation.line_id)
    )
    data = await query.gino.all()
    translation_count_per_line = {each[0]: each[1] for each in data}
    return translation_count_per_line


async def fetch_like_count(line_ids: List[int]) -> Dict[int, int]:
    """get like count per subtitle"""
    query = (
        db.select([LineLike.line_id, db.func.count(LineLike.line_id)])
        .where(LineLike.line_id.in_(line_ids))
        .group_by(LineLike.line_id)
    )

    data = await query.gino.all()
    return {each[0]: each[1] for each in data}


async def pick_user_liked(user_id: UUID, line_ids: List[int]) -> List[int]:
    """Pick user-liked subtitles"""
    query = db.select([LineLike.line_id]).where(
        db.and_(LineLike.user_id == user_id, LineLike.line_id.in_(line_ids))
    )
    data = await query.gino.all()
    return [each[0] for each in data]


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


async def fetch_by_content_id(
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
