from functools import wraps
import json
import asyncio

from alembic.config import Config
import click

from app import config, create_app
from app.services.user import create_user


def coroutine(f):
    """coroutine decorator"""

    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@click.group()
def cli():
    """
    Simple CLI For Managing Sanic App
    """
    pass


@cli.command(help="Show current revision")
def current():
    """
    Show current revision
    """
    from alembic.command import current

    alembic_ini_path = "./alembic.ini"
    alembic_cfg = Config(alembic_ini_path)

    current(alembic_cfg)


@cli.command(help="Show history revision")
def migrationshistory():
    """
    Show history revision
    """
    from alembic.command import history

    alembic_ini_path = "./alembic.ini"
    alembic_cfg = Config(alembic_ini_path)

    history(alembic_cfg)


@cli.command(help="Auto make migrations")
@click.option("-m", help="Migration message")
def makemigrations(m):
    """
    Auto make migrations
    """
    from alembic.command import revision

    alembic_ini_path = "./alembic.ini"
    alembic_cfg = Config(alembic_ini_path)
    alembic_cfg.set_main_option("db_url", config.DB_URL)

    revision_kwargs = {"autogenerate": True}
    if m is not None:
        revision_kwargs["message"] = m
    revision(alembic_cfg, **revision_kwargs)


@cli.command(help="Apply migrations")
def migrate():
    """
    Apply migrations
    """
    from alembic.command import upgrade

    alembic_ini_path = "./alembic.ini"
    alembic_cfg = Config(alembic_ini_path)
    alembic_cfg.set_main_option("db_url", config.DB_URL)

    upgrade(alembic_cfg, "head")


@cli.command(help="Downgrade")
@click.argument("revision", default="-1")
def downgrade(revision):
    """
    Apply migrations
    """
    from alembic.command import downgrade

    alembic_ini_path = "./alembic.ini"
    alembic_cfg = Config(alembic_ini_path)
    alembic_cfg.set_main_option("db_url", config.DB_URL)

    downgrade(alembic_cfg, revision)


@cli.command(help="set genres and categories")
@coroutine
async def init():
    """
    initializing the project
    :set categories and genres
    """
    from app import db
    from app.db_models import Category
    from app.db_models import Genre

    await db.set_bind(config.DB_URL)

    with open("data/categories.json") as f:
        categories = json.loads(f.read())

    # Insert Categories
    await Category.insert().gino.all(*categories)

    with open("data/genres.json") as f:
        genres = json.loads(f.read())

    # Insert Genres
    await Genre.insert().gino.all(*genres)


@cli.command(help="runserver")
def runserver():
    app = create_app()
    app.run(host="0.0.0.0", port=8000, debug=True)


@cli.command(help="Create Admin User")
@coroutine
async def create_admin():
    from app import db

    await db.set_bind(config.DB_URL)

    email = input("Email : ")
    nickname = input("Nickname : ")
    password = input("Password : ")
    password2 = input("Password Confirmation : ")

    if password != password2:
        raise Exception("Password does not match!")

    await create_user(email=email, nickname=nickname, password=password, is_admin=True)
    print(f"Successfully created admin : {nickname}")


if __name__ == "__main__":
    cli()
