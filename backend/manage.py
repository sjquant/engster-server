import os
import click
from alembic.config import Config
from app.utils.config import import_config_file


@click.group()
def cli():
    """
    Simple CLI For Managing Flask App
    """
    pass


@cli.command(help="Run Sanic server")
@click.option('--config', default=None, help="Set the settings.")
@click.option('-p', '--port', default=8000, help="Set the port where server runs.")
def runserver(port, config):
    """
    Run Sanic server
    """
    config_file = import_config_file(config)
    # It needs to be loaded after all config file loaded
    from app import create_app
    app = create_app(config_file)
    app.run(port=port, debug=app.config['DEBUG'])


@cli.command(help="Create admin user")
@click.option('--config', default=None, help="Set the settings.")
def creatsuperuser():
    """
    Create Admin User
    """
    config_file = import_config_file(config)
    # It needs to be loaded after all config file loaded
    from app import create_app
    app = create_app(config_file)


@cli.command(help="Show current revision")
@click.option('--config', default=None, help="Set the settings.")
def current(config):
    """
    Show current revision
    """
    from alembic.command import current
    config = import_config_file(config)

    alembic_ini_path = os.path.join(config.BASE_DIR, 'alembic.ini')
    alembic_cfg = Config(alembic_ini_path)

    current(alembic_cfg)


@cli.command(help="Show history revision")
@click.option('--config', default=None, help="Set the settings.")
def migrationshistory(config):
    """
    Show history revision
    """
    from alembic.command import history
    config = import_config_file(config)

    alembic_ini_path = os.path.join(config.BASE_DIR, 'alembic.ini')
    alembic_cfg = Config(alembic_ini_path)

    history(alembic_cfg)


@cli.command(help="Auto make migrations")
@click.option("-m", help="Migration message")
@click.option('--config', default=None, help="Set the settings.")
def makemigrations(m, config):
    """
    Auto make migrations
    """
    from alembic.command import revision
    config = import_config_file(config)

    alembic_ini_path = os.path.join(config.BASE_DIR, 'alembic.ini')
    alembic_cfg = Config(alembic_ini_path)
    alembic_cfg.set_main_option('db_url', config.DB_URL)

    revision_kwargs = {'autogenerate': True}
    if m is not None:
        revision_kwargs['message'] = m
    revision(alembic_cfg, **revision_kwargs)


@cli.command(help="Apply migrations")
@click.option('--config', default=None, help="Set the settings.")
def migrate(config):
    """
    Apply migrations
    """
    from alembic.command import upgrade
    config = import_config_file(config)

    alembic_ini_path = os.path.join(config.BASE_DIR, 'alembic.ini')
    alembic_cfg = Config(alembic_ini_path)
    alembic_cfg.set_main_option('db_url', config.DB_URL)

    upgrade(alembic_cfg, "head")


if __name__ == '__main__':
    cli()
