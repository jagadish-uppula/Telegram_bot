import os
import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get configuration from environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_IDS = json.loads(os.getenv("ADMIN_IDS", "[7424561546, 6465108010]"))  # JSON array of admin IDs

# Cloud-friendly file storage (using a dictionary that persists in memory)
# Note: For production, consider using a database like SQLite or Firebase
files_data = {}

def load_files():
    """Load files data from a JSON string in environment variable"""
    global files_data
    files_json = os.getenv("FILES_JSON", "{}")
    try:
        files_data = json.loads(files_json)
    except json.JSONDecodeError:
        files_data = {}
    return files_data

def save_files():
    """Save files data back to environment variable (conceptually)"""
    # In a real deployment, you would save to a database
    # For Choreo, you might want to use their configuration management
    # or connect to an external database
    global files_data
    return json.dumps(files_data)

# Initialize files data
files_data = load_files()

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello! Send me a keyword to find a document, or use /help for more options.")

# /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "/start - Start the bot\n"
        "/help - Show help text\n"
        "/addfile - Admins can add files to the database\n"
        "Search for files by sending keywords. Click on the listed files to open their Google Drive links."
    )

# /addfile command for admins to add new files
async def addfile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if user_id not in ADMIN_IDS:
        await update.message.reply_text("You are not authorized to add files.")
        logger.warning(f"Unauthorized access attempt by user {user_id}")
        return

    if len(context.args) < 3:
        await update.message.reply_text(
            "Usage:\n\n/addfile <keyword> <file_name> <google_drive_link>\n\n"
            "Example:\n/addfile report Project_Report.pdf https://drive.google.com/file/d/1234567890/view"
        )
        return

    keyword = context.args[0].lower()
    file_name = context.args[1]
    google_drive_link = context.args[2]

    if keyword not in files_data:
        files_data[keyword] = []

    files_data[keyword].append({"name": file_name, "link": google_drive_link})
    save_files()

    await update.message.reply_text(f"File '{file_name}' added under keyword '{keyword}' successfully.")
    logger.info(f"Admin {user_id} added file '{file_name}' under keyword '{keyword}'.")

# Search for files and send clickable Google Drive links
async def search_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.message.text.strip().lower()
    matches = []

    for keyword, files in files_data.items():
        for file in files:
            file_name = file['name'].replace('_', '').lower()
            if query in file_name or query in keyword:
                matches.append(file)

    if matches:
        keyboard = [
            [InlineKeyboardButton(f"{file['name']}", url=file["link"])] for file in matches
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Click on a file to view/download it:", reply_markup=reply_markup
        )
        logger.info(f"Sent search results to {update.effective_user.username}")
    else:
        await update.message.reply_text("Sorry, no documents found matching your query.")
        logger.info(f"No match for: {query}")

def main():
    # Create the Application instance
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("addfile", addfile))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_document))

    # Run the bot
    logger.info("Starting the bot...")
    application.run_polling()

if __name__ == "__main__":
    main()
  
