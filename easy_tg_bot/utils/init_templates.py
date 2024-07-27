import os
import shutil
import logging


# Consts
DRAFTS_FOLDER = "templates"
DRAFTS_FOLDER_PATH = os.path.join(
    os.path.dirname(__file__), DRAFTS_FOLDER
)


def initialize_file_from_draft(file_name):
    # Debug
    if not os.path.exists(DRAFTS_FOLDER_PATH):
        logging.error(f"Templates folder '{DRAFTS_FOLDER_PATH}' does not exist.")
        return

    draft_path = os.path.join(DRAFTS_FOLDER_PATH, file_name)
    if not os.path.exists(draft_path):
        logging.error(f"{draft_path} does not exist.")
        return 

    # Create files
    current_directory = os.getcwd()
    output_file = os.path.join(current_directory, file_name)
    if not os.path.exists(output_file):
        shutil.copy(draft_path, output_file)
        logging.info(f"{file_name} file created.")

        # The unfilled config
        if file_name == ".env":
            raise ValueError("Please fill the .env file and try again.")

    return True


def initialize_all_files_from_drafts():
    return all(
        initialize_file_from_draft(file_name)
        for file_name in os.listdir(DRAFTS_FOLDER_PATH)
    )
