import os
import shutil


# Consts
DRAFTS_FOLDER = "templates"
DRAFTS_FOLDER_PATH = os.path.join(
    os.path.dirname(__file__), DRAFTS_FOLDER
)


def initialize_file_from_draft(file_name, root_dir):
    # Create files
    if not os.path.exists(root_dir):
        os.makedirs(root_dir)

    output_file = os.path.join(root_dir, file_name)
    if os.path.exists(output_file):
        return

    # Debug
    if not os.path.exists(DRAFTS_FOLDER_PATH):
        print(f"Templates folder '{DRAFTS_FOLDER_PATH}' does not exist.")
        return

    draft_path = os.path.join(DRAFTS_FOLDER_PATH, file_name)
    if not os.path.exists(draft_path):
        print(f"{draft_path} does not exist.")
        return 

    # Create files
    shutil.copy(draft_path, output_file)
    print(f"{file_name} file created.")

    return True


def create_vultr_deploy_yml_from_draft():
    github_actions_folder = ".github/workflows"
    github_actions_folder_path = os.path.join(
        os.getcwd() , github_actions_folder
    )
    if not os.path.exists(github_actions_folder_path):
        os.makedirs(github_actions_folder_path)

    deploy_yml_draft = "deploy.yml"
    deploy_yml_output_path = os.path.join(github_actions_folder_path, deploy_yml_draft)
    if os.path.exists(deploy_yml_output_path):
        return
    
    deploy_yml_path = os.path.join(DRAFTS_FOLDER_PATH, deploy_yml_draft)
    if not os.path.exists(deploy_yml_path):
        print(f"{deploy_yml_path} does not exist.")
        return

    shutil.copy(deploy_yml_path, deploy_yml_output_path)
    print(f"deploy.yml created in {github_actions_folder_path}.")
