import click
import os

from .mylogging import logger
from .utils.init_templates import initialize_file_from_draft
from . import settings
from .utils.run_docker_polling import run_container, create_yaml_file


# Main
@click.group()
@click.version_option()
def cli():
    """The CLI tool."""


# Utils
def clear_env_variables():
    """
    Clears all environment variables set by the .env file.
    Relevant keys start with "TG_".
    """
    for key in os.environ:
        if key.startswith("TG_"):
            os.putenv(key, "")
            print(f"CLEARED ENV: {key}")


# Builds neccessary files for the developer and runs polling
@click.option("--upd-env", is_flag=True, help="Clear old env. var. configuration")
@click.option("--docker", is_flag=True, help="Deploy as a Docker container; env vars from .env")
@cli.command()
def run(upd_env, docker):
    if upd_env:
        clear_env_variables()

        root_dir = settings.TG_FILE_FOLDER_PATH or os.getcwd()
        initialize_file_from_draft("settings.py", root_dir)
        initialize_file_from_draft("text.xlsx", root_dir)
        initialize_file_from_draft("main.py", root_dir)
        initialize_file_from_draft(".gitignore", root_dir)

    elif docker:
        root_dir = settings.TG_FILE_FOLDER_PATH or os.getcwd()
        initialize_file_from_draft("settings.py", root_dir)
        initialize_file_from_draft("text.xlsx", root_dir)
        initialize_file_from_draft("main.py", root_dir)
        initialize_file_from_draft(".gitignore", root_dir)
        initialize_file_from_draft("Dockerfile", root_dir)
        initialize_file_from_draft(".dockerignore", root_dir)
        create_yaml_file()
        run_container()
        return

    # poetry ads
    try:
        os.system("poetry run python main.py")
    except Exception as e:
        logger.error(
            "Please install poetry, or launch main.py directly yourself. Sorry!"
        )


# Set the webhook for a Telegram Bot
@click.option("--token", default=settings.TG_BOT_TOKEN)
@click.option("--url", default=settings.TG_WEBHOOK_URL)
@cli.command()
def set_webhook(token, url):
    os.system(f"curl -X POST https://api.telegram.org/bot{token}/setWebhook?url={url}")


# Developer mode
if __name__ == "__main__":
    cli()
