from typing import List, Optional

from sqlalchemy.dialects.postgresql import UUID

from app import db
from app.utils import PBKDF2PasswordHasher


class BaseModel(db.Model):
    def to_dict(self, show: Optional[List[str]] = None, hide: List[str] = []):
        """
        Transform model into dict

        params
        ----------
        show: columns to transform into dict
        """

        if show is None:
            return {
                each.name: getattr(self, each.name)
                for each in self.__table__.columns
                if each.name not in hide
            }
        else:
            return {
                each.name: getattr(self, each.name)
                for each in self.__table__.columns
                if each.name in show and each.name not in hide
            }


class TimeStampedModel(BaseModel):

    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
    )


class User(TimeStampedModel):
    """ User Model for storing user related details """

    __tablename__ = "user"

    id = db.Column(UUID, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    nickname = db.Column(db.String(12), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    photo = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hasher = PBKDF2PasswordHasher()

    def __repr__(self):
        return "<User {}>".format(self.email)

    def set_password(self, password: str):
        self.password_hash = self.hasher.create_password(password)

    def check_password(self, password: str) -> bool:
        """ check password """
        return self.hasher.verify_password(password, self.password_hash)

    def to_dict(self, **kwargs):
        kwargs["hide"] = ["password_hash"]
        return super().to_dict(**kwargs)


class Content(BaseModel):

    __tablename__ = "content"

    id = db.Column(db.Integer, db.Sequence("content_id_seq"), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    year = db.Column(db.String(4), nullable=False)
    poster = db.Column(db.String(255))

    _id_idx = db.Index("content_idx_id", "id")
    _title_idx = db.Index("content_idx_title", "title")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Genre(BaseModel):

    __tablename__ = "genre"

    id = db.Column(db.Integer, db.Sequence("genre_id_seq"), primary_key=True)
    genre = db.Column(db.String(50), nullable=False, unique=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ContentXGenre(BaseModel):

    __tablename__ = "content_genre"

    content_id = db.Column(
        db.Integer, db.ForeignKey("content.id", ondelete="CASCADE"), nullable=False
    )
    genre_id = db.Column(
        db.Integer, db.ForeignKey("genre.id", ondelete="CASCADE"), nullable=False
    )

    _unique = db.UniqueConstraint("content_id", "genre_id", name="content_genre_unique")


class Subtitle(BaseModel):

    __tablename__ = "subtitle"

    id = db.Column(db.Integer, db.Sequence("line_id_seq"), primary_key=True)
    line = db.Column(db.Text, nullable=False)
    time = db.Column(db.Integer)  # time as seconds
    content_id = db.Column(db.Integer, db.ForeignKey("content.id"), nullable=False)

    _id_idx = db.Index("line_idx_id", "id")
    _line_idx = db.Index("line_idx_line", "line")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class SubtitleLike(TimeStampedModel):

    __tablename__ = "line_like"

    id = db.Column("id", db.Integer, db.Sequence("line_like_id_seq"), primary_key=True)
    user_id = db.Column(UUID, db.ForeignKey("user.id", ondelete="CASCADE"))
    line_id = db.Column(db.Integer, db.ForeignKey("subtitle.id", ondelete="CASCADE"))

    _id_idx = db.Index("line_like_idx_id", "id")
    _unique = db.UniqueConstraint("user_id", "line_id", name="line_like_unique")


class Translation(TimeStampedModel):

    __tablename__ = "translation"

    id = db.Column(db.Integer, db.Sequence("translation_id_seq"), primary_key=True)
    translation = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="PENDING")
    line_id = db.Column(
        db.Integer, db.ForeignKey("subtitle.id", ondelete="CASCADE"), nullable=False
    )
    user_id = db.Column(UUID, db.ForeignKey("user.id", ondelete="CASCADE"))

    _id_idx = db.Index("translation_idx_id", "id")
    _translation_idx = db.Index("translation_idx_translation", "translation")


class TranslationLike(TimeStampedModel):

    __tablename__ = "translation_like"

    id = db.Column(
        "id", db.Integer, db.Sequence("translation_like_id_seq"), primary_key=True
    )
    user_id = db.Column(UUID, db.ForeignKey("user.id", ondelete="CASCADE"))
    translation_id = db.Column(
        db.Integer, db.ForeignKey("translation.id", ondelete="CASCADE"), nullable=False
    )

    _id_idx = db.Index("translation_like_idx_id", "id")
    _unique = db.UniqueConstraint(
        "user_id", "translation_id", name="translation_like_unique"
    )


class TranslationReview(TimeStampedModel):

    __tablename__ = "translation_review"

    id = db.Column(
        "id", db.Integer, db.Sequence("translation_review_id_seq"), primary_key=True
    )
    status = db.Column(db.String(20), default="PENDING")
    translation = db.Column(db.Text, nullable=False)
    message = db.Column(db.String(400))
    translation_id = db.Column(
        db.Integer, db.ForeignKey("translation.id", ondelete="CASCADE"), nullable=False
    )
    reviewer_id = db.Column(UUID, db.ForeignKey("user.id"))
