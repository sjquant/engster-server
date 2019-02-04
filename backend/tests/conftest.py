
import pytest

from app import create_app
from app.utils.config import set_env


@pytest.yield_fixture
def app():
    set_env('test')
    from app import create_app
    app = create_app('test')
    yield app


@pytest.fixture
def test_cli(loop, app, test_client):
    return loop.run_until_complete(test_client(app))
