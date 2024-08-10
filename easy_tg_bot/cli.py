import click
import os

from .utils.init_templates import initialize_all_files_from_drafts
from .mylogging import logger
from .settings import initialize_env, TG_BOT_TOKEN, WEBHOOK_URL


@click.group()
@click.version_option()
def cli():
    """The CLI tool."""

@click.option('--no-init', is_flag=True, help="Do not initialize .env")
@cli.command()
def run(no_init):
    """poetry ads"""
    if not no_init:
        # refresh settings
        initialize_env()
        from . import settings 
        # the rest of the files
        initialize_all_files_from_drafts()

    try:
        os.system("poetry run python main.py")

    except Exception as e:
        logger.error("Please install poetry, or launch main.py directly yourself. Sorry!")


# Set the webhook for a Telegram Bot
@click.option("--token", default=TG_BOT_TOKEN)
@click.option("--url", default=WEBHOOK_URL)
@cli.command()
def set_webhook(token, url):
    os.system(f"curl -X POST https://api.telegram.org/bot{token}/setWebhook?url={url}")


# Developer mode
if __name__ == "__main__":
    cli()
