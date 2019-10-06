from sqlalchemy.dialects.postgresql import UUID

from app import db
from app.utils.models import BaseModel, TimeStampedModel


class Content(BaseModel):

    __tablename__ = "content"

    id = db.Column(db.Integer, db.Sequence("content_id_seq"), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    year = db.Column(db.String(4), nullable=False)
    reference = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return "<Content {}>".format(self.title)


class Category(BaseModel):

    __tablename__ = "category"

    id = db.Column(db.Integer, db.Sequence("category_id_seq"), primary_key=True)
    category = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return "<Category {}>".format(self.category)


class Genre(BaseModel):

    __tablename__ = "genre"

    id = db.Column(db.Integer, db.Sequence("genre_id_seq"), primary_key=True)
    genre = db.Column(db.String(50), nullable=False, unique=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return "<Genre {}>".format(self.genre)


class ContentXGenre(BaseModel):

    __tablename__ = "content_genre"

    content_id = db.Column(
        db.Integer, db.ForeignKey("content.id", ondelete="CASCADE"), nullable=False
    )
    genre_id = db.Column(
        db.Integer, db.ForeignKey("genre.id", ondelete="CASCADE"), nullable=False
    )


class Line(BaseModel):

    __tablename__ = "line"

    id = db.Column(db.Integer, db.Sequence("line_id_seq"), primary_key=True)
    line = db.Column(db.Text, nullable=False)
    time = db.Column(db.Time)
    content_id = db.Column(db.Integer, db.ForeignKey("content.id"), nullable=False)

    _idx = db.Index("line_idx_line", "line")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return "<Line {}>".format(self.line)


class LineLike(TimeStampedModel):

    __tablename__ = "line_like"

    id = db.Column("id", db.Integer, db.Sequence("line_like_id_seq"), primary_key=True)
    user_id = db.Column(UUID, db.ForeignKey("user.id"))
    line_id = db.Column(db.Integer, db.ForeignKey("line.id"))

    _unique = db.UniqueConstraint("user_id", "line_id", name="line_like_unique")

    def __repr__(self):
        return "<Line Like {}>".format(self.id)


class Translation(TimeStampedModel):

    __tablename__ = "translation"

    id = db.Column(db.Integer, db.Sequence("translation_id_seq"), primary_key=True)
    translation = db.Column(db.Text, nullable=False)
    line_id = db.Column(db.Integer, db.ForeignKey("line.id"), nullable=False)
    translator_id = db.Column(UUID, db.ForeignKey("user.id"))
    is_accepted = db.Column(
        db.Boolean, server_default="f", default=False, nullable=False
    )

    _idx = db.Index("translation_idx_translation", "translation")

    def __repr__(self):
        return "<Translation {}>".format(self.translation)


class TranslationLike(TimeStampedModel):

    __tablename__ = "translation_like"

    id = db.Column(
        "id", db.Integer, db.Sequence("translation_like_id_seq"), primary_key=True
    )
    user_id = db.Column(UUID, db.ForeignKey("user.id"))
    translation_id = db.Column(
        db.Integer, db.ForeignKey("translation.id"), nullable=False
    )

    _unique = db.UniqueConstraint(
        "user_id", "translation_id", name="translation_like_unique"
    )

    def __repr__(self):
        return "<Translation Like {}>".format(self.id)
