from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import assistant
import json
from tools import FileTools

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hello! This is your bot speaking.')

async def run_script(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Your script logic here
    print('Script executed.')
    await update.message.reply_text('Script executed.')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # This function will print any text message sent to the bot
    message_text = update.message.text
    print("User: " + message_text)
    response = assistant.answer(message_text)
    await update.message.reply_text(response)

def main() -> None:
    application = Application.builder().token('6473136092:AAFmUfm5NWJsgQ9J4GLcaFMAhWE42KLx8BY').build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('run', run_script))
    # Adding a handler for non-command messages using filters.TEXT to only capture text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()

