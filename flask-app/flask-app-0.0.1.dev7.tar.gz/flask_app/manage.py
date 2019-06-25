from flask.cli import FlaskGroup

from app import create_app

app = create_app()
cli = FlaskGroup(create_app=create_app, load_dotenv=True)


if __name__ == "__main__":
    cli()
