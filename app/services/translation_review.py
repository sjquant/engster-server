from typing import List, Dict, Any, Optional

from app.models import (
    Subtitle,
    Translation,
    TranslationReview,
    User,
)
from app import db
from app.utils import fetch_all


async def fetch(
    status: Optional[List[str]] = None, limit: int = 20, cursor: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Fetch translation reviews

    Args:
        status: statuses to filter. If None, fetch all statuses
        limit: limit
        cursor: cursor
    """
    conditions = []

    if cursor:
        conditions.append(TranslationReview.id < cursor)

    if status:
        conditions.append(TranslationReview.status.in_(status))

    query = (
        db.select(
            [
                TranslationReview,
                User.nickname.label("reviewer"),
                Subtitle.id.label("subtitle_id"),
                Subtitle.line.label("subtitle"),
            ]
        )
        .select_from(
            TranslationReview.join(User, TranslationReview.reviewer_id == User.id)
            .join(Translation, TranslationReview.translation_id == Translation.id)
            .join(Subtitle, Translation.line_id == Subtitle.id)
        )
        .order_by(TranslationReview.id.desc())
        .limit(limit)
    )

    if conditions:
        query = query.where(db.and_(*conditions))

    data = await fetch_all(query)
    return data
