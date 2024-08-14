import yaml
import os
from .. import settings


IMG_NAME = str(settings.TG_BOT_NAME).lower()


# Utils
def create_yaml_file(version="3.12", image_name=IMG_NAME):
    # Define the structure of your Docker Compose YAML
    keys = read_env_keys()
    docker_compose_config = {
        "version": version,
        "name": image_name,
        "services": {
            "app": {
                "image": f"{image_name}",
                "environment": [
                    f"{key}=${{{key}}}" for key in keys
                ],
            }
        },
    }
    # Write to a file
    path = os.path.join(os.getcwd(), "docker-compose.yml")
    with open(path, "w") as file:
        yaml.dump(docker_compose_config, file, default_flow_style=False)
    print("Docker Compose YAML file has been created.")


def read_env_keys():
    """Load environment variables from a .env file."""
    env_keys = []
    path = os.path.join(os.getcwd(), ".env")
    with open(path, "r") as file:
        for line in file:
            if line.strip() and not line.startswith("#"):
                key, _ = line.strip().split("=", 1)
                env_keys.append(key)
    return env_keys


def run_container():
    dockerfile = os.path.join(os.getcwd(), "Dockerfile")
    tag=f"{IMG_NAME}:latest"
    context = "."
    build_command = f"docker build -f {dockerfile} -t {tag} {context}"
    print(f"Executing: {build_command}")
    build_status = os.system(build_command)
    if build_status != 0:
        print("Failed to build Docker image.")
        return
    run_command = f"docker-compose up"
    print(f"Executing: {run_command}")
    run_status = os.system(run_command)
    if run_status != 0:
        print("Failed to run Docker container.")
        return
    print("Container started successfully.")
