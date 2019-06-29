import math
from sqlalchemy.sql.elements import BinaryExpression
from app import db


async def calc_max_page(page_size: int, condition: BinaryExpression) -> int:
    """ Calculate Max Page """
    count = await db.select([db.func.count()]).where(condition).gino.scalar()
    return math.ceil(count / page_size)
