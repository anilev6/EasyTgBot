import pandas as pd

from .mylogging import logger
from . import settings


DEFAULT_TEXT_FILE = settings.TG_FILE_FOLDER_PATH + "text.xlsx"
PARSE_MODE_COLUMN = "PARSE MODE"
INDEX_COLUMN = "TEXT INDEX"
VALIDATION_MESSAGE = "validate_text_{}"  # text.xlsx
DEFAULT_NOT_FOUND_TEXT = "404"
IGNORE_ABSENSE_TEXT_STRINGS = ["intro_video_caption"]

NECCESSARY_COLUMNS = [PARSE_MODE_COLUMN, INDEX_COLUMN]
NECCESSARY_SHEETS = []


def clear_table_element(element):
    element = element.strip() if isinstance(element, str) else element
    if not element:
        element = pd.NA
    return element


def validate_dataframes(file_path, sheets, columns):
    df_sheets = pd.read_excel(file_path, sheet_name=None, dtype=str)

    if not all(s in df_sheets for s in sheets):
        msg = "Sheets in the file are missing!"
        raise ValueError(msg)

    if not all(column in v.columns for column in columns for v in df_sheets.values()):
        msg = "Wrong columns in the file!"
        raise ValueError(msg)

    column_names = [df.columns.tolist() for df in df_sheets.values()]
    if not all(columns == column_names[0] for columns in column_names):
        msg = "Column names are different in different sheets."
        raise ValueError(msg)


# Get rid of spaces
def read_file(file_path) -> dict:
    # Initial validation
    validate_dataframes(
        file_path,
        NECCESSARY_SHEETS,
        NECCESSARY_COLUMNS,
    )

    df_sheets = pd.read_excel(file_path, sheet_name=None, dtype=str, index_col=0)

    # Clear strings
    for k, v in df_sheets.items():

        # Strip whitespace from all string data in the DataFrame
        v = v.map(clear_table_element)

        # Strip whitespace from column names
        v.columns = v.columns.map(clear_table_element)

        # Strip whitespace from index names
        v.index = v.index.map(clear_table_element)
        v.index_name = INDEX_COLUMN

        # Drop rows where the index is empty
        v = v.dropna(axis=0, how="all")

        df_sheets[k] = v

    return df_sheets


def get_text_dictionary(file_name=DEFAULT_TEXT_FILE):
    df = pd.concat(read_file(file_name).values(), axis=0)
    return {column: {index: value for index, value in df[column].dropna().items()} for column in df.columns if not df[column].dropna().empty}


def get_languages_from_dict(text_dictionary):
    return [lan for lan in text_dictionary.keys() if lan != PARSE_MODE_COLUMN]


def get_main_language_from_dict(text_dictionary):
    return get_languages_from_dict(text_dictionary)[0]


def get_parse_mode_from_dict(text_dictionary, text_string_index):
    # All the languages have the same parse mode
    return text_dictionary.get(PARSE_MODE_COLUMN,{}).get(text_string_index)


def get_text_from_dict(language, text_dictionary, text_string_index):
    result = text_dictionary.get(language, {}).get(text_string_index)
    if result is None:
        main_bot_language = get_main_language_from_dict(text_dictionary)
        result = text_dictionary.get(main_bot_language,{}).get(text_string_index)
        if result is None:
            if text_string_index not in IGNORE_ABSENSE_TEXT_STRINGS:
                logger.error(f"Key Error in file_dict: {text_string_index}")
            return DEFAULT_NOT_FOUND_TEXT
    return result


def get_text_and_parse_mode_from_dict(language, text_dictionary, text_string_index):
    return get_text_from_dict(
        language, text_dictionary, text_string_index
    ), get_parse_mode_from_dict(text_dictionary, text_string_index)


def validate_text_file(file_path) -> tuple:
    # Success
    code = 200
    try:
        TEXT_DICT = get_text_dictionary(file_path)
        LANS = get_languages_from_dict(TEXT_DICT)
        MAIN_LAN = get_main_language_from_dict(TEXT_DICT)
        # TODO parse mode and text example

    except Exception as e:
        # Validation error
        code = 400
        logger.error(str(e))

    finally:
        result = code, VALIDATION_MESSAGE.format(code)
        logger.info(result[1])
        return result


if __name__ == "__main__":
    # Test the file reading
    print(get_text_dictionary())#["English"])
    print(validate_text_file(DEFAULT_TEXT_FILE))
