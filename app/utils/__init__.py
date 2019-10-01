from typing import Tuple
import math
from sqlalchemy.sql.elements import BinaryExpression
from app import db


async def calc_max_page(page_size: int, condition: BinaryExpression) -> Tuple[int, int]:
    """
    Calculate Max Page

    Args:
        page_size: page size
        condition: gino conditional expression used in where

    Returns:
        max_page: maximum page
        count: total count
    """
    try:
        count = await db.select([db.func.count()]).where(condition).gino.scalar()
    except AttributeError:
        return 0, 0
    return math.ceil(count / page_size), count
