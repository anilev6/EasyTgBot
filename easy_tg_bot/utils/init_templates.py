import os
import shutil
import logging


# Consts
DRAFTS_FOLDER = "templates"
DRAFTS_FOLDER_PATH = os.path.join(
    os.path.dirname(__file__), DRAFTS_FOLDER
)


def initialize_file_from_draft(file_name, root_dir):
    # Create files
    output_file = os.path.join(root_dir, file_name)
    if os.path.exists(output_file):
        return

    # Debug
    if not os.path.exists(DRAFTS_FOLDER_PATH):
        logging.error(f"Templates folder '{DRAFTS_FOLDER_PATH}' does not exist.")
        return

    draft_path = os.path.join(DRAFTS_FOLDER_PATH, file_name)
    if not os.path.exists(draft_path):
        logging.error(f"{draft_path} does not exist.")
        return 

    # Create files
    shutil.copy(draft_path, output_file)
    logging.info(f"{file_name} file created.")

    return True


def initialize_all_files_from_drafts(root_dir):
    return all(
        initialize_file_from_draft(file_name, root_dir)
        for file_name in os.listdir(DRAFTS_FOLDER_PATH)
    )
