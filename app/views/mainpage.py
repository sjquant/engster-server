from sqlalchemy import select

from app import db
from app.libs.view import APIView
from app.libs.view_mixins import ListModelMixin
from app.db_models import MainContent


class MainContentListView(APIView, ListModelMixin):

    page_size: int = 15

    def get_query(self):
        return select(
            [
                MainContent.c.id,
                MainContent.c.title,
                MainContent.c.photo,
                MainContent.c.description,
                MainContent.c.issued_at,
            ]
        )

    def get(self, request):
        return await self.list(request)


class MainContentDetailView(APIView):
    def get(self, request):
        pass
