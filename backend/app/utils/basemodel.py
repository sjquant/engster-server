from typing import List, Optional
from app import db


class BaseModel(db.Model):

    def to_dict(self, show: Optional[List[str]] = None):
        """
        transform columns into dict

        params
        ----------
        show: columns to transform into dict
        """

        if show is None:
            return {each.name: getattr(self, each.name) for each in self.__table__.columns}

        else:
            return {each: getattr(self, each) for each in show}
