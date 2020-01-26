from typing import List, Dict
from app import db
from app.db_models import TranslationLike, LineLike


async def get_english_like_count(line_ids: List[int]) -> Dict[int, int]:
    """ get like count for lines """
    query = (
        db.select([LineLike.line_id, db.func.count(LineLike.line_id)])
        .where(LineLike.line_id.in_(line_ids))
        .group_by(LineLike.line_id)
    )

    res = await query.gino.all()
    data = {each[0]: each[1] for each in res}
    return data


async def get_korean_like_count(translation_ids: List[int]) -> Dict[int, int]:
    """ get korean count for translations """
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
    res = await query.gino.all()
    data = {each[0]: each[1] for each in res}
    return data


async def get_user_liked_english_lines(user_id, line_ids: List[int]) -> List[int]:
    query = db.select([LineLike.line_id]).where(
        db.and_(LineLike.user_id == user_id, LineLike.line_id.in_(line_ids))
    )
    res = await query.gino.all()
    return [each[0] for each in res]


async def get_user_liked_korean_lines(user_id, translation_ids: List[int]) -> List[int]:
    query = db.select([TranslationLike.translation_id]).where(
        db.and_(
            TranslationLike.user_id == user_id,
            TranslationLike.translation_id.in_(translation_ids),
        )
    )
    res = await query.gino.all()
    return [each[0] for each in res]
