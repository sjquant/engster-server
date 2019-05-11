import os
import click
from alembic.config import Config
from app.utils.config import get_config


@click.group()
def cli():
    """
    Simple CLI For Managing Sanic App
    """
    pass


@cli.command(help="Run Sanic server")
@click.option('--env', default='local', help="Set the settings.")
@click.option('-p', '--port', default=8000, help="Set the port where server runs.")
def runserver(port, env):
    """
    Run Sanic server
    """
    from app import create_app
    app = create_app(env)
    app.run(port=port, debug=app.config['DEBUG'])


@cli.command(help="Create admin user")
@click.option('--env', default='local', help="Set the settings.")
def creatsuperuser(env):
    """
    Create Admin User
    """
    config = get_config(env)
    # It needs to be loaded after all config file loaded
    from app import create_app
    app = create_app(config)


@cli.command(help="Show current revision")
@click.option('--env', default=None, help="Set the settings.")
def current(env):
    """
    Show current revision
    """
    from alembic.command import current

    config = get_config(env)

    alembic_ini_path = os.path.join(config.BASE_DIR, 'alembic.ini')
    alembic_cfg = Config(alembic_ini_path)

    current(alembic_cfg)


@cli.command(help="Show history revision")
@click.option('--env', default='local', help="Set the settings.")
def migrationshistory(env):
    """
    Show history revision
    """
    from alembic.command import history
    config = get_config(env)
    print(config.BASE_DIR)
    alembic_ini_path = os.path.join(config.BASE_DIR, 'alembic.ini')
    alembic_cfg = Config(alembic_ini_path)

    history(alembic_cfg)


@cli.command(help="Auto make migrations")
@click.option("-m", help="Migration message")
@click.option('--env', default='local', help="Set the settings.")
def makemigrations(m, env):
    """
    Auto make migrations
    """
    from alembic.command import revision
    config = get_config(env)
    alembic_ini_path = os.path.join(config.BASE_DIR, 'alembic.ini')
    alembic_cfg = Config(alembic_ini_path)
    alembic_cfg.set_main_option('db_url', config.DB_URL)

    revision_kwargs = {'autogenerate': True}
    if m is not None:
        revision_kwargs['message'] = m
    revision(alembic_cfg, **revision_kwargs)


@cli.command(help="Apply migrations")
@click.option('--env', default='local', help="Set the settings.")
def migrate(env):
    """
    Apply migrations
    """
    from alembic.command import upgrade
    config = get_config(env)

    alembic_ini_path = os.path.join(config.BASE_DIR, 'alembic.ini')
    alembic_cfg = Config(alembic_ini_path)
    alembic_cfg.set_main_option('db_url', config.DB_URL)

    upgrade(alembic_cfg, "head")


@cli.command(help="Downgrade")
@click.option('--env', default='local', help="Set the settings.")
@click.argument('revision', default='-1')
def downgrade(env, revision):
    """
    Apply migrations
    """
    from alembic.command import downgrade
    config = get_config(env)

    alembic_ini_path = os.path.join(config.BASE_DIR, 'alembic.ini')
    alembic_cfg = Config(alembic_ini_path)
    alembic_cfg.set_main_option('db_url', config.DB_URL)

    downgrade(alembic_cfg, revision)


if __name__ == '__main__':
    cli()
