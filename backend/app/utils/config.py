from app.core.exceptions import UnknownKeyword


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
