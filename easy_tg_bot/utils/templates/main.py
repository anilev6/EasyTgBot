import easy_tg_bot
# initiate other modules
import settings


@easy_tg_bot.command()
async def help(update, context):
    return await easy_tg_bot.send_text(update, context, "help_message")  # text.xlsx

if __name__=="__main__":
    easy_tg_bot.start.START_DONE_CALLBACK = help
    easy_tg_bot.telegram_bot_polling()
