from typing import List, Dict, Any

from app.models import Genre


async def fetch_all() -> List[Dict[str, Any]]:
    """Fetch all genres"""
    data = await Genre.query.gino.all()
    return [each.to_dict() for each in data]


async def get_by_id(genre_id: int) -> Genre:
    genre = await Genre.query.where(Genre.id == genre_id).gino.first()
    return genre
