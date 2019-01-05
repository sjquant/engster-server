
from app.core.exceptions import UnknownKeyword
import click


@click.group()
def cli():
    """
    Simple CLI For Managing Flask App
    """
    pass


def import_config_file(config: str):
    config = config if config else 'local'

    if config == 'local':
        import app.config.local as config_file
    elif config == 'test':
        import app.config.test as config_file
    elif config == 'production':
        import app.config.production as config_file
    else:
        raise UnknownKeyword(config)
    return config_file


@cli.command(help="Run Sanic server")
@click.option('--config', default=None, help="Set the settings.")
@click.option('-p', '--port', default=8000, help="Set the port where server runs.")
@click.option('-p', '--port', default=8000, help="Set the port where server runs.")
def runserver(port, config):

    config_file = import_config_file(config)
    # It needs to be loaded after all config file loaded
    from app import create_app
    app = create_app(config_file)
    app.run(port=port, debug=app.config['DEBUG'])


if __name__ == '__main__':
    cli()
