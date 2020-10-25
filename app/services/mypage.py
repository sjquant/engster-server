from typing import List, Dict, Any, Optional
from uuid import UUID
from app.db_models import (
    Line,
    Translation,
    User,
    Content,
    LineLike,
    TranslationLike,
)
from app import db
from app import config
from app.exceptions import DataDoesNotExist
from app.utils import get_photo_url


async def get_user_activitiy_summary(user_id: UUID) -> Dict[str, Any]:
    query = (
        db.select([User.nickname, User.photo, db.func.count(Translation.id)])
        .select_from(User.outerjoin(Translation))
        .where(User.id == user_id)
        .group_by(User.id)
    )
    data = await query.gino.first()
    if data:
        data = {
            "user_id": user_id,
            "user_nickname": data[0],
            "user_photo": get_photo_url(data[1], media_url=config.MEDIA_URL),
            "translation_count": data[2],
        }
    else:
        raise DataDoesNotExist("User activity summary does not exist.")
    return data


async def fetch_user_liked_english_lines(
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
                Content.id,
                Content.title,
                Content.year,
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
    columns = (
        "id",
        "line",
        "content_id",
        "content_title",
        "content_year",
        "liked_at",
    )
    data = await query.gino.all()
    return [dict(zip(columns, each)) for each in data]


async def fetch_user_liked_korean_lines(
    user_id: UUID, limit: int = 20, cursor: Optional[int] = None
) -> List[Dict["str", Any]]:
    condition = (
        db.and_(TranslationLike.id < cursor, TranslationLike.user_id == user_id)
        if cursor
        else TranslationLike.user_id == user_id
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
                TranslationLike.created_at,
            ]
        )
        .where(condition)
        .select_from(
            Translation.join(Line, Translation.line_id == Line.id)
            .join(Content, Line.content_id == Content.id)
            .join(TranslationLike, Translation.id == TranslationLike.translation_id)
        )
        .limit(limit)
        .order_by(TranslationLike.id.desc())
    )

    columns = (
        "id",
        "translation",
        "line_id",
        "line",
        "content_id",
        "content_title",
        "content_year",
        "liked_at",
    )
    data = await query.gino.all()
    return [dict(zip(columns, each)) for each in data]


async def fetch_user_translations(
    user_id: UUID, limit: int = 20, cursor: Optional[int] = None
) -> List[Dict["str", Any]]:
    condition = (
        db.and_(Translation.id < cursor, Translation.user_id == user_id)
        if cursor
        else Translation.user_id == user_id
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
            ]
        )
        .where(condition)
        .select_from(
            Translation.join(Line, Translation.line_id == Line.id).join(
                Content, Line.content_id == Content.id
            )
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
    )
    data = await query.gino.all()
    return [dict(zip(columns, each)) for each in data]
