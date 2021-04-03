from typing import List, Dict, Any, Optional
from uuid import UUID

from app.models import (
    Subtitle,
    Translation,
    Content,
    TranslationLike,
    TranslationReview,
    User,
)
from app import db
from app.schemas import TranslationReviewStatus
from app.utils import fetch_all


async def fetch(
    status: Optional[List[TranslationReviewStatus]] = None,
    limit: int = 20,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    query = (
        db.select([Translation, Subtitle.line, User.nickname.label("user_nickname")])
        .select_from(
            Translation.join(Subtitle, Translation.line_id == Subtitle.id).join(
                User, Translation.user_id == User.id, isouter=True
            )
        )
        .order_by(Translation.id.desc())
        .limit(limit)
        .offset(offset)
    )
    if status:
        query = query.where(Translation.status.in_(status))

    data = await fetch_all(query)
    return data


async def search(keyword: str, limit: int = 20, cursor: Optional[int] = None):
    """Search Korean with a keyword"""
    conditions = [
        Translation.translation.op("~*")(keyword),
        Translation.status == "APPROVED",
    ]
    if cursor:
        conditions.append(Translation.id < cursor)

    query = (
        db.select(
            [
                Translation.id,
                Translation.translation,
                Subtitle.id.label("line_id"),
                Subtitle.line,
                Subtitle.time,
                Content.id.label("content_id"),
                Content.title.label("content_title"),
                Content.year.label("content_year"),
            ]
        )
        .where(db.and_(*conditions))
        .select_from(
            Translation.join(Subtitle, Translation.line_id == Subtitle.id).join(
                Content, Subtitle.content_id == Content.id
            )
        )
        .limit(limit)
        .order_by(Translation.id.desc())
    )

    data = await fetch_all(query)
    return data


async def count(keyword: str) -> int:
    """Count translations"""
    query = db.select([db.func.count(Translation.id)]).where(
        Translation.translation.op("~*")(keyword)
    )
    return await query.gino.scalar()


async def get_by_id(translation_id: int) -> Translation:
    query = Translation.query.where(db.and_(Translation.id == translation_id))
    translation = await query.gino.first()
    return translation


async def fetch_user_liked(
    user_id: UUID, limit: int = 20, cursor: Optional[int] = None
) -> List[Dict[str, Any]]:
    conditions = [TranslationLike.user_id == user_id]
    if cursor:
        conditions.append(TranslationLike.id < cursor)

    query = (
        db.select(
            [
                Translation.id,
                Translation.translation,
                Subtitle.id.label("line_id"),
                Subtitle.line,
                Subtitle.time,
                Content.id.label("content_id"),
                Content.title.label("content_title"),
                Content.year.label("content_year"),
                TranslationLike.created_at,
            ]
        )
        .where(db.and_(*conditions))
        .select_from(
            Translation.join(Subtitle, Translation.line_id == Subtitle.id)
            .join(Content, Subtitle.content_id == Content.id)
            .join(TranslationLike, Translation.id == TranslationLike.translation_id)
        )
        .limit(limit)
        .order_by(TranslationLike.id.desc())
    )

    data = await fetch_all(query)
    return data


async def fetch_user_written(
    user_id: UUID, limit: int = 20, cursor: Optional[int] = None
) -> List[Dict[str, Any]]:
    conditions = [Translation.user_id == user_id]
    if cursor:
        conditions.append(Translation.id < cursor)

    query = (
        db.select(
            [
                Translation.id,
                Translation.translation,
                Subtitle.id.label("line_id"),
                Subtitle.line,
                Subtitle.time,
                Content.id.label("content_id"),
                Content.title.label("content_title"),
                Content.year.label("content_year"),
            ]
        )
        .where(db.and_(*conditions))
        .select_from(
            Translation.join(Subtitle, Translation.line_id == Subtitle.id).join(
                Content, Subtitle.content_id == Content.id
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


async def fetch_like_count(translation_ids: List[int]) -> Dict[int, int]:
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


async def change_status(
    translation_id: int, status: str, reviewer_id: str, message: Optional[str] = None
):
    if status not in {"PENDING", "APPROVED", "CHANGE_REQUESTED", "REJECTED"}:
        raise ValueError("Invalid status")

    async with db.transaction():
        translation = await Translation.query.where(
            Translation.id == translation_id
        ).gino.first()
        if not translation:
            raise ValueError("Translation not found")
        await translation.update(status=status).apply()
        await TranslationReview(
            status=status,
            translation=translation.translation,
            message=message,
            translation_id=translation.id,
            reviewer_id=reviewer_id,
        ).create()


async def count_reviews(translation_id: int) -> int:
    """Count reviews for a translation"""
    query = db.select([db.func.count(TranslationReview.id)]).where(
        TranslationReview.translation_id == translation_id
    )
    return await query.gino.scalar()


async def fetch_reviews(
    translation_id: int, limit: int, offset: int = 0
) -> List[Dict[str, Any]]:
    """Fetch reviews for a translation"""
    conditions = [TranslationReview.translation_id == translation_id]

    query = (
        db.select([TranslationReview, User.nickname.label("reviewer_nickname")])
        .where(db.and_(*conditions))
        .select_from(
            TranslationReview.join(User, TranslationReview.reviewer_id == User.id)
        )
        .order_by(TranslationReview.id.desc())
        .limit(limit)
        .offset(offset)
    )

    data = await fetch_all(query)
    return data
