
import pytest

from app import create_app
from app.utils.config import get_config


@pytest.yield_fixture
def app():
    get_config('test')
    from app import create_app
    app = create_app('test')
    yield app


@pytest.fixture
def test_cli(loop, app, test_client):
    return loop.run_until_complete(test_client(app))
