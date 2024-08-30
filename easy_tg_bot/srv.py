# Server utils
import os
import click
from .settings import get_secret


@click.group()
@click.version_option()
def srv():
    """The server utils CLI tool."""


def files_from_server_to_my_windows(remote_path, local_path, user, ip, debug=False):
    """requires ssh key to be set up"""
    command = f"scp -r  {user}@{ip}:{remote_path} {local_path}"
    if debug:
        print(command)
    os.system(command)


def files_from_my_windows_to_server(remote_path, local_path, user, ip, debug=False):
    """requires ssh key to be set up"""
    command = f"scp -r {local_path} {user}@{ip}:{remote_path}"
    if debug:
        print(command)
    os.system(command)


@click.option("--debug", is_flag=True, help="Print the command to the console")
@srv.command()
def bring_files_from_server(debug):
    """requires ssh key to be set up"""
    local_path = get_secret("LOCAL_PATH")
    remote_path = get_secret("REMOTE_PATH")
    user = get_secret("SERVER_USER")
    ip = get_secret("SERVER_IP")
    return files_from_server_to_my_windows(remote_path, local_path, user, ip, debug)


@click.option("--debug", is_flag=True, help="Print the command to the console")
@srv.command()
def bring_files_to_server(debug):
    """requires ssh key to be set up"""
    local_path = get_secret("LOCAL_PATH")
    remote_path = get_secret("REMOTE_PATH")
    user = get_secret("SERVER_USER")
    ip = get_secret("SERVER_IP")
    return files_from_my_windows_to_server(remote_path, local_path, user, ip, debug)
