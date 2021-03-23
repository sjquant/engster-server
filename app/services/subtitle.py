from typing import List, Dict, Any, Optional
from uuid import UUID

from app import db
from app.models import (
    User,
    Subtitle,
    Translation,
    Content,
    SubtitleLike,
)
from app.utils import fetch_all


async def search(keyword: str, limit: int = 20, cursor: Optional[int] = None):
    """Search English with a keyword"""
    conditions = [Subtitle.line.op("~*")(keyword)]
    if cursor:
        conditions.append(Subtitle.id < cursor)

    query = (
        db.select(
            [
                Subtitle.id,
                Subtitle.line,
                Subtitle.time,
                Content.id.label("content_id"),
                Content.title.label("content_title"),
                Content.year.label("content_year"),
            ]
        )
        .where(db.and_(*conditions))
        .select_from(Subtitle.join(Content, Subtitle.content_id == Content.id))
        .limit(limit)
        .order_by(Subtitle.id.desc())
    )

    data = await fetch_all(query)
    return data


async def count(keyword: str) -> int:
    """Count subtitles"""
    query = db.select([db.func.count(Subtitle.id)]).where(
        Subtitle.line.op("~*")(keyword)
    )
    return await query.gino.scalar()


async def pick_randomly(max_count=30) -> List[Optional[Dict[str, Any]]]:
    """Pick subtitles randomly

    Args:
        max_count: maximum length of subtitles to pick
    """
    total_count = await db.select([db.func.count(Subtitle.id)]).gino.scalar()
    if total_count == 0:
        return []

    percentage = max_count / total_count
    query = (
        db.select(
            [
                Subtitle.id,
                Subtitle.line,
                Subtitle.time,
                Translation.id.label("translation_id"),
                Translation.translation.label("translation"),
                Content.id.label("content_id"),
                Content.title.label("content_title"),
                Content.year.label("content_year"),
            ],
            distinct=Subtitle.id,
        )
        .select_from(
            Subtitle.join(Content, Subtitle.content_id == Content.id).join(
                Translation, Subtitle.id == Translation.line_id
            )
        )
        .where(db.func.random() < percentage)
    )

    data = await fetch_all(query)
    return data


async def add_like(line_id: int, user_id: UUID) -> SubtitleLike:
    like = SubtitleLike(line_id=line_id, user_id=user_id)
    await like.create()
    return like


async def remove_like(line_id: int, user_id: UUID) -> None:
    await SubtitleLike.delete.where(
        db.and_(SubtitleLike.line_id == line_id, SubtitleLike.user_id == user_id)
    ).gino.status()


async def fetch_user_liked(
    user_id: UUID, limit: int = 20, cursor: Optional[int] = 0
) -> List[Dict["str", Any]]:
    """Fetch subtitle a user liked"""
    conditions = [SubtitleLike.user_id == user_id]
    if cursor:
        conditions.append(SubtitleLike.id < cursor)

    query = (
        db.select(
            [
                Subtitle.id,
                Subtitle.line,
                Subtitle.time,
                Content.id.label("content_id"),
                Content.title.label("content_title"),
                Content.year.label("content_year"),
                SubtitleLike.created_at,
            ]
        )
        .where(db.and_(*conditions))
        .select_from(
            Subtitle.join(Content, Subtitle.content_id == Content.id).join(
                SubtitleLike, Subtitle.id == SubtitleLike.line_id
            )
        )
        .limit(limit)
        .order_by(SubtitleLike.id.desc())
    )

    data = await fetch_all(query)
    return data


async def fetch_translation_count(line_ids: List[int]) -> Dict[int, int]:
    """Get translation_count"""
    query = (
        db.select([Translation.line_id, db.func.count(Translation.line_id)])
        .where(
            db.and_(Translation.line_id.in_(line_ids), Translation.status != "REJECTED")
        )
        .group_by(Translation.line_id)
    )
    data = await query.gino.all()
    translation_count_per_line = {each[0]: each[1] for each in data}
    return translation_count_per_line


async def fetch_like_count(line_ids: List[int]) -> Dict[int, int]:
    """get like count per subtitle"""
    query = (
        db.select([SubtitleLike.line_id, db.func.count(SubtitleLike.line_id)])
        .where(SubtitleLike.line_id.in_(line_ids))
        .group_by(SubtitleLike.line_id)
    )

    data = await query.gino.all()
    return {each[0]: each[1] for each in data}


async def pick_user_liked(user_id: UUID, line_ids: List[int]) -> List[int]:
    """Pick user-liked subtitles"""
    query = db.select([SubtitleLike.line_id]).where(
        db.and_(SubtitleLike.user_id == user_id, SubtitleLike.line_id.in_(line_ids))
    )
    data = await query.gino.all()
    return [each[0] for each in data]


async def fetch_translations(
    line_id: int, limit: int = 15, cursor: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Fetch translations for give lines"""
    conditions = [
        Translation.line_id == line_id,
        Translation.status != "REJECTED",
    ]
    if cursor:
        conditions.append(Translation.id < cursor)

    query = (
        Translation.load(user=User.on(Translation.user_id == User.id))
        .query.where(db.and_(*conditions))
        .limit(limit)
        .order_by(Translation.id.desc())
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
    conditions = [
        Subtitle.content_id == content_id,
        Translation.user_id.is_(None),
    ]
    if cursor:
        conditions.append(Subtitle.id > cursor)

    query = (
        db.select(
            [
                Subtitle.id,
                Subtitle.line,
                Subtitle.time,
                Translation.id.label("translation_id"),
                Translation.translation.label("translation"),
                Content.id.label("content_id"),
                Content.title.label("content_title"),
                Content.year.label("content_year"),
            ],
            distinct=Subtitle.id,
        )
        .select_from(
            Subtitle.join(Content, Subtitle.content_id == Content.id).outerjoin(
                Translation, Subtitle.id == Translation.line_id
            )
        )
        .where(db.and_(*conditions))
        .order_by(Subtitle.id.asc())
        .limit(limit)
    )
    data = await fetch_all(query)
    return data


async def fetch_all_by_content_id(content_id: int) -> List[Dict[str, Any]]:
    """Fetch subtitle line ids of a content"""
    query = (
        db.select([Subtitle.id, Subtitle.line])
        .where(Subtitle.content_id == content_id)
        .order_by(Subtitle.id.asc())
    )
    data = await fetch_all(query)
    return data
