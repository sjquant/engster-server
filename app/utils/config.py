import os
import importlib

from app.utils.exceptions import UnknownKeyword


def set_env(env: str):
    if env.lower() not in ['local', 'test', 'production']:
        raise UnknownKeyword(env)
    os.environ['ENGSTER_ENV'] = env
    config = importlib.import_module(f"app.config.{env}")
    return config
