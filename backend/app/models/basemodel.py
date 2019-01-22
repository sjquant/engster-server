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
            return self.__values__

        else:
            return {each: self.__values__[each] for each in show}
