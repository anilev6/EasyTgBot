import click
import os

from .utils.init_templates import initialize_all_files_from_drafts
from .mylogging import logger


@click.group()
@click.version_option()
def cli():
    """The CLI tool."""


@cli.command()
def run():
    """poetry ads"""
    if initialize_all_files_from_drafts():
        try:
            os.system("poetry run python main.py")
        except Exception as e:
            logger.error("Please install poetry, or launch main.py directly yourself. Sorry!")


# Developer mode
if __name__ == "__main__":
    cli()
