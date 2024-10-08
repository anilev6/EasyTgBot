# Easy Telegram Bot 🎯 **easy-tg-bot**

This is my own Telegram bot framework for faster development and updating my bots.

*Based on [Python Telegram Bot](https://docs.python-telegram-bot.org/en/v21.4/).*

## Features

### Quick start

`easy-tg-bot run`

The command will create `.env` in your working directory if the file does not exist, and in this case you would have to fill it and try again.

Other necessary files are created if they do not exist, and finally `main.py` in your working directory is launched.

### Register commands with a decorator

```python
from easy_tg_bot import command

@command()
async def help(update, context):
    pass
```

### Text settings of the bot

By default, in the bot:

- Through `/admin` -> "⚙️ ...", admins regulate the settings of the bot via .xlsx file manipulation.

- All the bot text is stored in an exel file `text.xlsx` with "string_text_key":"value" structure, and the columns are the languages.

- To add a text, simply add a unique text index and the corresponding value in at least one language (the first column) in the `text.xlsx`.

- All the text info is preserved in the bot persistance.

- `from easytgbot import send_message` <- this async function accepts `update`, `context`, and "string_text_key" from the .xlsx file, as well as regular text = text, parse mode = ... etc.

- See `__init__.py` for more features.

### Other

Logs are rotating automatically.

See `main.py` generated by `easy-tg-bot run` command for more examples of usage.

## Installation

This is an installable Python package.

### PyPI

`poetry add easy-tg-bot` / `pip install easy-tg-bot` / any other manager command

### Poetry (manually from this folder)

Make sure poetry is installed. From this folder,

0. `poetry shell`; `poetry update`;

1. `poetry build`; `poetry install`;

## Usage

*! Fill the `.env` file in your working directory before or after this command*

`easy-tg-bot run` - run the bot (polling);
`easy-tg-bot run --docker` - deploy using .env file

In the bot if run is successful, try `/admin`.

Ctrl+C to exit.

`easy-tg-bot run` command runs "main.py" file, so one can as well run the file directly after it's created.

- `/admin` - admin panel

- `/start` -> makes user pick a language, agree to data_policy and share a phone number.

*See `main.py` for more details on how to configure the start coveration and explore /admin*

## # TODO

- Add more features description to `README` from `__init__.py`
