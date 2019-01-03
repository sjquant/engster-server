from sanic import Sanic
from sanic.response import json
import click


def create_app():
    app = Sanic()
    return app


def runserver():
    app = create_app()
    app.run()


def main():
    runserver()


if __name__ == '__main__':
    main()
