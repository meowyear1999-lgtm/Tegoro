import os
import re
import logging
from typing import List, Dict, Tuple
import telebot
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set")

bot = telebot.TeleBot(BOT_TOKEN)

# Custom User-Agent to avoid 403 errors
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Social media platforms for username enumeration
SOCIAL_PLATFORMS: List[Dict[str, str]] = [
    {"name": "GitHub", "url": "https://github.com/{username}"},
    {"name": "Instagram", "url": "https://www.instagram.com/{username}/"},
    {"name": "Twitter", "url": "https://twitter.com/{username}"},
    {"name": "Reddit", "url": "https://www.reddit.com/user/{username}"},
    {"name": "TikTok", "url": "https://www.tiktok.com/@{username}"},
    {"name": "YouTube", "url": "https://www.youtube.com/@{username}"},
    {"name": "LinkedIn", "url": "https://www.linkedin.com/in/{username}"},
    {"name": "Twitch", "url": "https://twitch.tv/{username}"},
    {"name": "Pinterest", "url": "https://www.pinterest.com/{username}"},
    {"name": "Snapchat", "url": "https://www.snapchat.com/add/{username}"},
    {"name": "Telegram", "url": "https://t.me/{username}"},
    {"name": "Discord", "url": "https://discord.com/users/{username}"},
    {"name": "BitBucket", "url": "https://bitbucket.org/{username}"},
    {"name": "GitLab", "url": "https://gitlab.com/{username}"},
    {"name": "Medium", "url": "https://medium.com/@{username}"},
    {"name": "Dev.to", "url": "https://dev.to/{username}"},
    {"name": "Patreon", "url": "https://www.patreon.com/{username}"},
    {"name": "Tumblr", "url": "https://{username}.tumblr.com"},
    {"name": "SoundCloud", "url": "https://soundcloud.com/{username}"},
    {"name": "Mastodon", "url": "https://mastodon.social/@{username}"},
]


def is_phone_number(text: str) -> bool:
    """
    Check if input is a phone number.
    Pattern: +?[0-9]{10,15}
    """
    pattern = r'^\+?[0-9]{10,15}$'
    return bool(re.match(pattern, text.strip()))


def is_username(text: str) -> bool:
    """
    Check if input is alphanumeric (username).
    """
    return bool(re.match(r'^[a-zA-Z0-9_.-]{3,32}$', text.strip()))


def check_username_presence(username: str) -> List[str]:
    """
    Check if username exists across social platforms.
    Returns a list of found platforms.
    """
    found_platforms = []
    headers = {"User-Agent": USER_AGENT}
    
    for platform in SOCIAL_PLATFORMS:
        try:
            url = platform["url"].format(username=username)
            response = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
            
            # Status codes that typically indicate user exists
            if response.status_code == 200:
                found_platforms.append(f"✅ [{platform['name']}]({url})")
                logger.info(f"Found {username} on {platform['name']}")
            elif response.status_code == 404:
                logger.info(f"{username} not found on {platform['name']}")
            else:
                logger.debug(f"{platform['name']}: Status {response.status_code}")
                
        except requests.Timeout:
            logger.warning(f"Timeout checking {platform['name']}")
        except requests.ConnectionError:
            logger.warning(f"Connection error checking {platform['name']}")
        except Exception as e:
            logger.error(f"Error checking {platform['name']}: {str(e)}")
    
    return found_platforms


def get_phone_info_mock(phone: str) -> Dict[str, str]:
    """
    Mock function to simulate HLR (Home Location Register) and carrier data lookup.
    In production, this would call real APIs.
    """
    # Normalize phone number
    phone_clean = re.sub(r'\D', '', phone)
    
    # Mock carrier detection based on country code
    carriers = {
        "1": ["AT&T", "Verizon", "T-Mobile", "Sprint"],  # USA/Canada
        "7": ["MTS", "Beeline", "MegaFon"],  # Russia
        "44": ["Vodafone", "EE", "O2"],  # UK
        "49": ["Telekom", "Vodafone", "Telefónica"],  # Germany
        "33": ["Orange", "SFR", "Bouygues"],  # France
    }
    
    # Extract country code (simplified)
    country_code = phone_clean[:1] if phone_clean.startswith("+") else phone_clean[:1]
    
    possible_carriers = carriers.get(country_code, ["Unknown Carrier"])
    
    return {
        "phone": phone,
        "status": "Active (Mock)",
        "carrier": possible_carriers[0],
        "country_code": f"+{country_code}",
        "possible_carriers": ", ".join(possible_carriers),
    }


def format_username_results(username: str, platforms: List[str]) -> str:
    """
    Format username search results in Markdown.
    """
    if not platforms:
        return f"❌ Username `{username}` not found on any platform."
    
    result = f"🔍 **Username Search Results for:** `{username}`\n\n"
    result += f"**Found on {len(platforms)} platform(s):**\n\n"
    result += "\n".join(platforms)
    
    return result


def format_phone_results(phone_info: Dict[str, str]) -> str:
    """
    Format phone number search results in Markdown.
    """
    result = f"📱 **Phone Number Analysis:** `{phone_info['phone']}`\n\n"
    result += f"**Status:** {phone_info['status']}\n"
    result += f"**Primary Carrier:** {phone_info['carrier']}\n"
    result += f"**Country Code:** {phone_info['country_code']}\n"
    result += f"**Possible Carriers:** {phone_info['possible_carriers']}\n\n"
    result += "📌 *Note: This is mock data. For real HLR lookup, integrate with premium APIs.*"
    
    return result


@bot.message_handler(content_types=['text'])
def handle_message(message):
    """
    Main message handler for all text messages.
    Automatically detects input type and processes accordingly.
    """
    try:
        user_input = message.text.strip()
        
        # Send processing indicator
        processing_msg = bot.send_message(
            message.chat.id,
            "⏳ Processing your request...",
            parse_mode="Markdown"
        )
        
        # Detect input type
        if is_phone_number(user_input):
            logger.info(f"Processing phone number: {user_input}")
            phone_info = get_phone_info_mock(user_input)
            result = format_phone_results(phone_info)
            
        elif is_username(user_input):
            logger.info(f"Processing username: {user_input}")
            bot.send_message(
                message.chat.id,
                f"🔍 Searching for `{user_input}` across platforms...",
                parse_mode="Markdown"
            )
            platforms = check_username_presence(user_input)
            result = format_username_results(user_input, platforms)
            
        else:
            result = (
                "❓ Invalid input. Please provide:\n\n"
                "📱 **Phone Number:** 10-15 digits (e.g., `+1234567890`)\n"
                "👤 **Username:** 3-32 alphanumeric characters (e.g., `johndoe`)"
            )
        
        # Delete processing message and send result
        bot.delete_message(message.chat.id, processing_msg.message_id)
        bot.send_message(message.chat.id, result, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error in handle_message: {str(e)}")
        bot.send_message(
            message.chat.id,
            f"❌ An error occurred: {str(e)}\n\nPlease try again.",
            parse_mode="Markdown"
        )


@bot.message_handler(commands=['start'])
def start_command(message):
    """
    Handle /start command.
    """
    welcome_text = (
        "👋 **Welcome to Sherlock Bot!**\n\n"
        "🔍 OSINT Tool for Username & Phone Number Reconnaissance\n\n"
        "**How to use:**\n\n"
        "📱 **Phone Number Search:**\n"
        "`+1234567890` or `1234567890` (10-15 digits)\n"
        "Returns: Carrier info & HLR status\n\n"
        "👤 **Username Search:**\n"
        "`johndoe` (3-32 alphanumeric characters)\n"
        "Returns: Presence across 20+ social platforms\n\n"
        "**Supported Platforms:**\n"
        "GitHub, Instagram, Twitter, Reddit, TikTok, YouTube, LinkedIn, Twitch, "
        "Pinterest, Snapchat, Telegram, Discord, BitBucket, GitLab, Medium, "
        "Dev.to, Patreon, Tumblr, SoundCloud, Mastodon\n\n"
        "⚠️ **Disclaimer:** Use responsibly. For educational purposes only."
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")


@bot.message_handler(commands=['help'])
def help_command(message):
    """
    Handle /help command.
    """
    help_text = (
        "**📖 Command List:**\n\n"
        "/start - Show welcome message\n"
        "/help - Show this help message\n\n"
        "**Input Examples:**\n"
        "`+1-800-555-0123` - Phone lookup\n"
        "`john_doe` - Username search\n\n"
        "**Platform Coverage:** 20+\n"
        "**Timeout per request:** 5 seconds\n"
        "**Max attempts:** Unlimited"
    )
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")


def main():
    """
    Main bot loop.
    """
    logger.info("🤖 Sherlock Bot started successfully")
    logger.info(f"Monitoring platforms: {len(SOCIAL_PLATFORMS)}")
    
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {str(e)}")
        main()  # Restart on error


if __name__ == "__main__":
    main()
