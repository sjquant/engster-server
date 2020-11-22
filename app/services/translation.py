from typing import List, Dict, Any, Optional
from uuid import UUID

from app.db_models import (
    Line,
    Translation,
    Content,
    TranslationLike,
)
from app import db
from app.utils import fetch_all


async def search(keyword: str, limit: int = 20, cursor: Optional[int] = None):
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

    data = await fetch_all(query)
    return data


async def get_by_id(translation_id: int) -> Translation:
    query = Translation.query.where(db.and_(Translation.id == translation_id))
    translation = await query.gino.first()
    return translation


async def fetch_user_liked(
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

    data = await fetch_all(query)
    return data


async def fetch_user_written(
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
    data = await fetch_all(query)
    return data


async def add_like(translation_id: int, user_id: UUID) -> TranslationLike:
    like = TranslationLike(translation_id=translation_id, user_id=user_id)
    await like.create()
    return like


async def remove_like(translation_id: int, user_id: UUID) -> None:
    await TranslationLike.delete.where(
        db.and_(
            TranslationLike.translation_id == translation_id,
            TranslationLike.user_id == user_id,
        )
    ).gino.status()


async def get_like_count(translation_ids: List[int]) -> Dict[int, int]:
    """get korean count per translation """
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


async def pick_user_liked(user_id: UUID, translation_ids: List[int]) -> List[int]:
    query = db.select([TranslationLike.translation_id]).where(
        db.and_(
            TranslationLike.user_id == user_id,
            TranslationLike.translation_id.in_(translation_ids),
        )
    )
    data = await query.gino.all()
    return [each[0] for each in data]
