from functools import wraps
import asyncio
import json
import os

from alembic.command import current, revision, history, upgrade, downgrade
from alembic.config import Config
import dotenv
import click

# Import app in each command functions to prevent config from prematurely being set


def coroutine(f):
    """coroutine decorator"""

    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@click.group()
@click.option("--env-file")
@click.pass_context
def cli(ctx, env_file):
    """Engster Command Line Interface"""
    ctx.ensure_object(dict)

    if env_file:
        if not os.path.exists(env_file):
            raise FileNotFoundError(f"{env_file} does not exists")
        dotenv.load_dotenv(env_file)
        print(f"Successfully Loaded {env_file}")

    from app import config

    alembic_ini_path = "./alembic.ini"
    alembic_cfg = Config(alembic_ini_path)
    alembic_cfg.set_main_option("db_url", config.DB_URL)
    ctx.obj["alembic_cfg"] = alembic_cfg


@cli.command(help="Show current revision")
@click.pass_context
def current_revision(ctx):
    """Show current revision"""
    alembic_cfg = ctx.obj["alembic_cfg"]
    current(alembic_cfg)


@cli.command()
@click.pass_context
def migrations_history(ctx):
    """Show revision history"""
    alembic_cfg = ctx.obj["alembic_cfg"]
    history(alembic_cfg)


@cli.command()
@click.option("--mesagae", "-m", help="Migration message")
@click.pass_context
def make_migrations(ctx, message):
    """Create migration file"""
    alembic_cfg = ctx.obj["alembic_cfg"]
    revision_kwargs = {"autogenerate": True}
    if message is not None:
        revision_kwargs["message"] = message
    revision(alembic_cfg, **revision_kwargs)
    print("Successfully created migration files")


@cli.command()
@click.pass_context
def migrate(ctx):
    """Apply migrations to database"""
    alembic_cfg = ctx.obj["alembic_cfg"]
    upgrade(alembic_cfg, "head")
    print("Successfully upgraded migrations")


@cli.command()
@click.argument("revision", default="-1")
@click.pass_context
def downgrade_revision(ctx, revision):
    """Downgrade revision"""
    from app import config

    alembic_cfg = ctx.obj["alembic_cfg"]
    alembic_cfg.set_main_option("db_url", config.DB_URL)

    downgrade(alembic_cfg, revision)
    print("Successfully downgraded migrations")


@cli.command()
@coroutine
@click.pass_context
async def init_genres(ctx):
    """Insert intial genres to database"""
    from app import db, config
    from app.models import Genre

    await db.set_bind(config.DB_URL)

    with open("data/genres.json") as f:
        genres = json.loads(f.read())

    # Insert Genres
    await Genre.insert().gino.all(*genres)
    print("Successfully inserted genres")


@cli.command()
def runserver():
    """Run server"""
    from app import create_app

    app = create_app()
    app.run(host="0.0.0.0", port=8000, debug=True)


@cli.command()
@coroutine
async def create_admin():
    """Create Admin User"""
    from app import db, config
    from app.services.user import create_user

    await db.set_bind(config.DB_URL)

    email = input("Email: ")
    nickname = input("Nickname: ")
    password = input("Password: ")
    password2 = input("Password Confirmation: ")

    if password != password2:
        raise Exception("Password does not match!")

    await create_user(email=email, nickname=nickname, password=password, is_admin=True)
    print(f"Successfully created admin: {nickname}")


if __name__ == "__main__":
    cli()
