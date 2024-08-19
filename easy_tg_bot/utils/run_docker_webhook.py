import os
from .. import settings

def get_env_keys():
    """Load environment variables from a .env file."""
    env_keys = []
    path = os.path.join(os.getcwd(), ".env")
    with open(path, "r") as file:
        for line in file:
            if line.strip() and not line.startswith("#"):
                env_keys.append(line.strip())
    return env_keys


def run_docker_container(image_name, host_port = 8000, host_dir = None):
    """
    Launches a Docker container with specified image, volume mapping, and environment variables.
    
    :param image_name: The name of the Docker image to use.
    :param volume_mapping: A list of tuples specifying the volume mappings (host_dir, container_dir).
    :param env_variables: A list of environment variables to set in the container.
    """
    port_mapping_str = f"-p {host_port}:8000"
    data_folder = settings.TG_FILE_FOLDER_PATH
    container_dir = "/usr/src/app/" + data_folder
    if host_dir is None:
        host_dir = os.path.join(os.getcwd(), data_folder)

    volume_mapping_str = f"-v {host_dir}:/usr/src/app/{container_dir}"
    env_variables_str = " ".join([f"-e {var}" for var in get_env_keys()])
    command = f"docker run {port_mapping_str} {volume_mapping_str} {env_variables_str} {image_name}"
    os.system(command)

def build_docker_image(name=settings.TG_BOT_NAME.lower(), tag = None):
    """
    Builds a Docker image from the current directory.
    """
    if tag is None:
        tag = "latest"

    tag = f"{name}:{tag}"
    context = "."
    command = f"docker build -t {tag} {context} --no-cache"
    os.system(command)
    return tag


def build_and_run(host_port: int = 8000, host_dir: str = None):
    """
    Builds a Docker image from the current directory and runs a container from it.
    """
    image_name = build_docker_image()
    run_docker_container(image_name, host_port, host_dir)
