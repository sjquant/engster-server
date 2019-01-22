from app import db
from app.models import BaseModel


class Line(BaseModel):

    __tablename__ = 'lines'

    id = db.Column(db.Integer, db.Sequence('line_id_seq'), primary_key=True)
    line = db.Column(db.Text, nullable=False)
    time = db.Column(db.Time, nullable=True)
    content_id = db.Column(db.Integer, db.ForeignKey('contents.id'))

    def __repr__(self):
        return '<Line {}>'.format(self.line)


class LineLike(BaseModel):

    __tablename__ = 'line_like'

    id = db.Column('id', db.Integer, db.Sequence(
        'line_like_seq'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    line_id = db.Column(db.Integer, db.ForeignKey('lines.id'))

    def __repr__(self):
        return '<Line Like {}>'.format(self.id)


class Translation(BaseModel):

    __tablename__ = 'translations'

    id = db.Column(db.Integer, db.Sequence(
        'translation_id_seq'), primary_key=True)
    translation = db.Column(db.Text, nullable=False)
    line_id = db.Column(db.Integer, db.ForeignKey('lines.id'))
    translator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    content_id = db.Column(db.Integer, db.ForeignKey('contents.id'))

    def __repr__(self):
        return '<Translations {}>'.format(self.translation)


class TranslationLike(BaseModel):

    __talbename__ = 'translation_like'

    id = db.Column('id', db.Integer, db.Sequence(
        'translation_like_seq'), primary_key=True)
    db.Column(db.Integer, db.ForeignKey('users.id'))
    db.Column(db.Integer, db.ForeignKey('translations.id'))

    def __repr__(self):
        return '<Translation Like {}>'.format(self.id)
