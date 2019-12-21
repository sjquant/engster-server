from sqlalchemy.dialects.postgresql import UUID, JSONB

from app import db
from .base_models import BaseModel


class MainContents(BaseModel):

    __tablename__ = "main_contents"

    id = db.Column(UUID, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    photo = db.Column(db.String(255), nullable=False)
    issued_at = db.Column(db.Date, server_default=db.func.now())
    data = db.Column(JSONB)

    def __repr__(self):
        return "<TodayKorean {}>".format(self.title)
