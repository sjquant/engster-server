import pytest

from app import create_app


@pytest.yield_fixture
def app():
    app = create_app()
    yield app


@pytest.fixture
def test_cli(loop, app, test_client):
    return loop.run_until_complete(test_client(app))
