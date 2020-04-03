from typing import List, Dict, Any
from uuid import UUID
from app.db_models import (
    Line,
    Translation,
    User,
    Content,
    Category,
    LineLike,
    TranslationLike,
)
from app import db


async def get_user_activitiy_summary(user_id: UUID) -> Dict[str, Any]:
    query = (
        db.select([db.func.count(Translation.id)])
        .select_from(User.join(Translation))
        .where(User.id == user_id)
        .group_by(User.id)
    )
    data = await query.gino.first()
    if data is None:
        data = {"user_id": user_id, "translation_count": 0}
    else:
        data = {"user_id": user_id, "translation_count": data[0]}
    return data


async def fetch_user_liked_english_lines(
    user_id: UUID, limit: int = 15, offset: int = 0
) -> List[Dict["str", Any]]:
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
                LineLike.created_at,
            ]
        )
        .where(LineLike.user_id == user_id)
        .select_from(
            Line.join(Content, Line.content_id == Content.id)
            .join(Category, Content.category_id == Category.id)
            .join(LineLike, Line.id == LineLike.line_id)
        )
        .limit(limit)
        .offset(offset)
        .order_by(LineLike.created_at.desc())
    )
    columns = (
        "id",
        "line",
        "content_id",
        "content_title",
        "content_year",
        "category_id",
        "category_name",
        "liked_at",
    )
    data = await query.gino.all()
    return [dict(zip(columns, each)) for each in data]


async def fetch_user_liked_korean_lines(
    user_id: UUID, limit: int = 15, offset: int = 0
) -> List[Dict["str", Any]]:
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
                TranslationLike.created_at,
            ]
        )
        .where(TranslationLike.user_id == user_id)
        .select_from(
            Translation.join(Line, Translation.line_id == Line.id)
            .join(Content, Line.content_id, Content.id)
            .join(Category, Content.category_id == Category.id)
            .join(TranslationLike, Translation.id == TranslationLike.translation_id)
        )
        .limit(limit)
        .offset(offset)
        .order_by(TranslationLike.created_at.desc())
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
        "liked_at",
    )
    data = await query.gino.all()
    return [dict(zip(columns, each)) for each in data]


async def fetch_user_translations(
    user_id: UUID, limit: int = 15, offset: int = 0
) -> List[Dict["str", Any]]:
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
        .where(Translation.user_id == user_id)
        .select_from(
            Translation.join(Line, Translation.line_id == Line.id)
            .join(Content, Line.content_id == Content.id)
            .join(Category, Content.category_id == Category.id)
        )
        .limit(limit)
        .offset(offset)
        .order_by(Translation.created_at.desc())
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
