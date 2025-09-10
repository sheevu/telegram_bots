import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Bot token from environment
BOT_TOKEN = os.getenv('BOT_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    welcome_message = (
        "🤖 Welcome! I'm your friendly AI concierge bot.\n\n"
        "Here's what I can help you with:\n"
        "• /help - Show all available commands\n"
        "• /love - Get today's love quote\n"
        "• /poetry - Receive a romantic quote\n"
        "• /song - Get a song suggestion\n"
        "• /advice - Daily helpful tip\n"
        "• /mood - Quick mood check-in\n\n"
        "You can also just chat with me naturally!"
    )
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = (
        "🆘 **Available Commands:**\n\n"
        "🌟 /start - Welcome message and intro\n"
        "❓ /help - Show this help message\n"
        "💕 /love - Today's love quote via AI\n"
        "🎭 /poetry - Short romantic quote\n"
        "🎵 /song - Song recommendation\n"
        "💡 /advice - Daily helpful tip\n"
        "😊 /mood - Simple mood check-in\n\n"
        "💬 You can also send me any message and I'll respond as your friendly AI concierge!"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def get_openai_response(prompt: str) -> str:
    """Get response from OpenAI API."""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a friendly, warm, and helpful AI concierge. Keep responses concise but heartfelt."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return "Sorry, I'm having trouble connecting to my AI brain right now. Please try again later! 🤖"

async def love_quote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send today's love quote."""
    prompt = "Generate a beautiful, inspiring love quote for today. Make it heartwarming and meaningful."
    quote = await get_openai_response(prompt)
    await update.message.reply_text(f"💕 **Today's Love Quote:**\n\n{quote}\n\n✨ _Spread love wherever you go!_", parse_mode='Markdown')

async def poetry_quote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a short romantic quote."""
    prompt = "Create a short, beautiful romantic quote or line of poetry. Keep it elegant and touching."
    quote = await get_openai_response(prompt)
    await update.message.reply_text(f"🎭 **Romantic Quote:**\n\n_{quote}_\n\n💝 _For the romantic soul_", parse_mode='Markdown')

async def song_suggestion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Suggest a song."""
    prompt = "Suggest a great song (artist and title) with a brief reason why it's worth listening to. Make it uplifting or meaningful."
    suggestion = await get_openai_response(prompt)
    await update.message.reply_text(f"🎵 **Song Suggestion:**\n\n{suggestion}\n\n🎶 _Enjoy the music!_", parse_mode='Markdown')

async def daily_advice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Give daily advice."""
    prompt = "Share a practical, positive daily life tip or advice. Make it actionable and encouraging."
    advice = await get_openai_response(prompt)
    await update.message.reply_text(f"💡 **Daily Advice:**\n\n{advice}\n\n🌟 _You've got this!_", parse_mode='Markdown')

async def mood_checkin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Simple mood check-in."""
    mood_message = (
        "😊 **Mood Check-in**\n\n"
        "How are you feeling today?\n\n"
        "Remember:\n"
        "• It's okay to have ups and downs\n"
        "• Every day is a fresh start\n"
        "• You're doing better than you think!\n\n"
        "💪 Tell me what's on your mind, I'm here to listen!"
    )
    await update.message.reply_text(mood_message, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular messages with AI concierge response."""
    user_message = update.message.text
    user_name = update.effective_user.first_name or "friend"
    
    prompt = f"As a friendly AI concierge, respond warmly to this message from {user_name}: '{user_message}'. Be helpful, encouraging, and personable."
    response = await get_openai_response(prompt)
    
    await update.message.reply_text(f"🤖 {response}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("love", love_quote))
    application.add_handler(CommandHandler("poetry", poetry_quote))
    application.add_handler(CommandHandler("song", song_suggestion))
    application.add_handler(CommandHandler("advice", daily_advice))
    application.add_handler(CommandHandler("mood", mood_checkin))
    
    # Handle regular messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Register error handler
    application.add_error_handler(error_handler)

    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
