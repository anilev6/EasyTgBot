import click
import os

from .mylogging import logger
from .utils.init_templates import initialize_file_from_draft, create_vultr_deploy_yml_from_draft
from . import settings


# Main
@click.group()
@click.version_option()
def cli():
    """The CLI tool."""


# Builds neccessary files for the developer and runs polling
@click.option("--docker", is_flag=True, help="Deploy as a Docker container; env vars from .env")
@cli.command()
def run(docker):
    root_dir = "./data"
    initialize_file_from_draft("text.xlsx", root_dir)

    root_dir = os.getcwd()
    initialize_file_from_draft("settings.py", root_dir)
    initialize_file_from_draft("main.py", root_dir)
    initialize_file_from_draft(".gitignore", root_dir)
    if docker:
        initialize_file_from_draft("Dockerfile", root_dir)
        initialize_file_from_draft(".dockerignore", root_dir)
        initialize_file_from_draft("docker-compose.yml", root_dir)
        run_command = f"docker-compose up"
        print(f"Executing: {run_command}")
        run_status = os.system(run_command)
        if run_status != 0:
            print("Failed to run Docker container.")
            return
        print("Container started successfully.")
        return
    # poetry ads
    try:
        os.system("poetry run python main.py")
    except Exception as e:
        logger.error(f"Please install poetry, or launch main.py directly yourself. Sorry! Error:\n{e}")


# Get the webhook info for a Telegram Bot
@click.option("--token", default=settings.BOT_TOKEN)
@cli.command()
def get_webhook_info(token):
    os.system(f"curl -X POST https://api.telegram.org/bot{token}/getWebhookInfo")


# Generate a secret token for Telegram
@cli.command()
def generate_secret_token():
    import secrets
    token = secrets.token_hex(16)
    logger.info(f"Generated secret token: {token}")


@cli.command()
def vultr():
    """Deploys to Vultr using Actions."""
    root_dir = os.getcwd()
    initialize_file_from_draft("Dockerfile", root_dir)
    initialize_file_from_draft(".dockerignore", root_dir)
    initialize_file_from_draft("docker-compose.yml", root_dir)
    create_vultr_deploy_yml_from_draft()


# Developer mode
if __name__ == "__main__":
    cli()
