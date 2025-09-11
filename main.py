import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI
from dotenv import load_dotenv
import asyncio
from typing import Optional

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize OpenAI client with error handling
try:
    client = OpenAI(
        api_key=os.getenv('OPENAI_API_KEY'),
        timeout=30.0,  # Add timeout for better reliability
    )
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {e}")
    client = None

# Bot token from environment
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Validate environment variables
if not BOT_TOKEN:
    logger.error("BOT_TOKEN not found in environment variables")
    raise ValueError("BOT_TOKEN is required")

if not os.getenv('OPENAI_API_KEY'):
    logger.error("OPENAI_API_KEY not found in environment variables")
    raise ValueError("OPENAI_API_KEY is required")

# System prompt for better AI responses
SYSTEM_PROMPT = (
    "You are a friendly, warm, and helpful AI concierge bot. "
    "Keep responses concise but heartfelt and engaging. "
    "Be supportive, encouraging, and personable in your interactions. "
    "Provide practical advice when asked and maintain a positive tone."
)

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

async def get_openai_response(prompt: str, max_tokens: int = 150) -> str:
    """Get response from OpenAI API with improved error handling and modern API usage."""
    if not client:
        return "Sorry, AI service is currently unavailable. Please try again later! 🤖"
    
    try:
        # Use the modern OpenAI API with better parameters
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-3.5-turbo",  # Can be upgraded to gpt-4 for better responses
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            timeout=30
        )
        
        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content.strip()
        else:
            return "I'm having trouble generating a response right now. Please try again! 🤖"
            
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        error_messages = [
            "Sorry, I'm having trouble connecting to my AI brain right now. Please try again later! 🤖",
            "Oops! My AI circuits are a bit tangled right now. Give me a moment and try again! ⚡",
            "My AI brain needs a quick reboot! Please try your request again in a moment. 🔄"
        ]
        import random
        return random.choice(error_messages)

async def love_quote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send today's love quote."""
    prompt = "Generate a beautiful, inspiring love quote for today. Make it heartwarming, meaningful, and uplifting."
    quote = await get_openai_response(prompt)
    await update.message.reply_text(
        f"💕 **Today's Love Quote:**\n\n{quote}\n\n✨ _Spread love wherever you go!_", 
        parse_mode='Markdown'
    )

async def poetry_quote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a short romantic quote."""
    prompt = "Create a short, beautiful romantic quote or line of poetry. Keep it elegant, touching, and memorable."
    quote = await get_openai_response(prompt)
    await update.message.reply_text(
        f"🎭 **Romantic Quote:**\n\n_{quote}_\n\n💝 _For the romantic soul_", 
        parse_mode='Markdown'
    )

async def song_suggestion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Suggest a song."""
    prompt = "Suggest a great song (artist and title) with a brief reason why it's worth listening to. Make it uplifting, meaningful, or emotionally resonant."
    suggestion = await get_openai_response(prompt)
    await update.message.reply_text(
        f"🎵 **Song Suggestion:**\n\n{suggestion}\n\n🎶 _Enjoy the music!_", 
        parse_mode='Markdown'
    )

async def daily_advice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Give daily advice."""
    prompt = "Share a practical, positive daily life tip or advice. Make it actionable, encouraging, and genuinely helpful for personal growth."
    advice = await get_openai_response(prompt)
    await update.message.reply_text(
        f"💡 **Daily Advice:**\n\n{advice}\n\n🌟 _You've got this!_", 
        parse_mode='Markdown'
    )

async def mood_checkin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Simple mood check-in with encouraging message."""
    mood_message = (
        "😊 **Mood Check-in**\n\n"
        "How are you feeling today?\n\n"
        "Remember:\n"
        "• It's okay to have ups and downs\n"
        "• Every day is a fresh start\n"
        "• You're doing better than you think!\n"
        "• Small steps lead to big changes\n\n"
        "💪 Tell me what's on your mind, I'm here to listen and help!"
    )
    await update.message.reply_text(mood_message, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular messages with AI concierge response."""
    if not update.message or not update.message.text:
        return
        
    user_message = update.message.text
    user_name = update.effective_user.first_name or "friend"
    
    # Enhanced prompt for better contextual responses
    prompt = (
        f"As a friendly AI concierge, respond warmly to this message from {user_name}: '{user_message}'. "
        f"Be helpful, encouraging, personable, and provide practical value when possible. "
        f"If they're asking for help or advice, provide actionable suggestions. "
        f"If they're sharing something, respond empathetically and engagingly."
    )
    
    response = await get_openai_response(prompt, max_tokens=200)
    await update.message.reply_text(f"🤖 {response}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a user-friendly message."""
    logger.error("Exception while handling an update:", exc_info=context.error)
    
    # If we have access to the update, send a friendly error message
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "🔧 Oops! Something went wrong on my end. Please try again in a moment. "
            "If the issue persists, try using /help to see available commands! 🤖"
        )

def main() -> None:
    """Start the bot with improved configuration."""
    logger.info("Starting Telegram bot...")
    
    # Create the Application with better configuration
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .connect_timeout(30)
        .read_timeout(30)
        .write_timeout(30)
        .build()
    )
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("love", love_quote))
    application.add_handler(CommandHandler("poetry", poetry_quote))
    application.add_handler(CommandHandler("song", song_suggestion))
    application.add_handler(CommandHandler("advice", daily_advice))
    application.add_handler(CommandHandler("mood", mood_checkin))
    
    # Handle regular messages (non-commands)
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    
    # Register error handler
    application.add_error_handler(error_handler)
    
    logger.info("Bot handlers registered successfully")
    
    # Run the bot with polling
    try:
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True  # Clear any pending updates on startup
        )
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        raise

if __name__ == '__main__':
    main()
