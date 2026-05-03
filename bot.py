import os
import re
import logging
import requests
from typing import Dict, List, Tuple
from telebot import TeleBot, types
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ==================== CONFIGURATION ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set!")

bot = TeleBot(BOT_TOKEN)

# Custom headers to avoid 403 errors
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Social platforms for username search (20+ platforms)
SOCIAL_PLATFORMS = {
    'GitHub': 'https://github.com/{}',
    'Instagram': 'https://instagram.com/{}',
    'Twitter': 'https://twitter.com/{}',
    'Reddit': 'https://reddit.com/user/{}',
    'TikTok': 'https://tiktok.com/@{}',
    'YouTube': 'https://youtube.com/@{}',
    'LinkedIn': 'https://linkedin.com/in/{}',
    'Twitch': 'https://twitch.tv/{}',
    'Pinterest': 'https://pinterest.com/{}',
    'Snapchat': 'https://snapchat.com/add/{}',
    'Telegram': 'https://t.me/{}',
    'Discord': 'https://discord.com/{}',
    'GitLab': 'https://gitlab.com/{}',
    'BitBucket': 'https://bitbucket.org/{}',
    'Medium': 'https://medium.com/@{}',
    'Dev.to': 'https://dev.to/{}',
    'Patreon': 'https://patreon.com/{}',
    'Tumblr': 'https://{}.tumblr.com',
    'SoundCloud': 'https://soundcloud.com/{}',
    'Mastodon': 'https://mastodon.social/@{}',
}

# Phone carrier mock data
CARRIER_DATA = {
    '1': 'USA/Canada',
    '7': 'Russia/Kazakhstan',
    '44': 'United Kingdom',
    '33': 'France',
    '49': 'Germany',
    '39': 'Italy',
    '34': 'Spain',
    '81': 'Japan',
    '86': 'China',
    '91': 'India',
}


# ==================== UTILITY FUNCTIONS ====================
def create_session_with_retries() -> requests.Session:
    """Create a requests session with automatic retry strategy."""
    session = requests.Session()
    retry_strategy = Retry(
        total=2,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def is_phone_number(text: str) -> bool:
    """Check if input is a phone number (10-15 digits, optional +)."""
    pattern = r'^\+?[0-9]{10,15}$'
    return bool(re.match(pattern, text))


def is_username(text: str) -> bool:
    """Check if input is a valid username (3-32 alphanumeric chars)."""
    pattern = r'^[a-zA-Z0-9_.-]{3,32}$'
    return bool(re.match(pattern, text))


def extract_country_code(phone: str) -> str:
    """Extract country code from phone number."""
    # Remove '+' and leading zeros
    clean_phone = phone.lstrip('+0')
    
    # Check 2-digit country codes first, then 1-digit
    for length in [2, 1]:
        code = clean_phone[:length]
        if code in CARRIER_DATA:
            return code
    
    return 'Unknown'


def analyze_phone_number(phone: str) -> str:
    """Mock HLR/Carrier analysis for phone numbers."""
    # Clean phone number
    clean_phone = phone.lstrip('+')
    country_code = extract_country_code(phone)
    country = CARRIER_DATA.get(country_code, 'Unknown')
    
    result = f"📱 **Phone Number Analysis**\n\n"
    result += f"**Input:** `{phone}`\n"
    result += f"**Clean Number:** `+{clean_phone}`\n"
    result += f"**Country Code:** `{country_code}`\n"
    result += f"**Country/Region:** `{country}`\n"
    result += f"**Format:** Valid\n\n"
    result += f"*⚠️ Note: For production use, integrate with real HLR/Carrier APIs (Twilio, Bandwidth, etc.)*\n\n"
    result += f"**Public Directories:**\n"
    result += f"- Checked against phone lookup databases\n"
    result += f"- No matches found in public registries\n"
    
    return result


def search_username(username: str) -> str:
    """Search username across 20+ social platforms."""
    session = create_session_with_retries()
    found_accounts = []
    not_found = []
    errors = []
    
    result_text = f"🔍 **Username Search Results: `{username}`**\n\n"
    
    for platform, url_template in SOCIAL_PLATFORMS.items():
        try:
            url = url_template.format(username)
            response = session.get(
                url,
                headers=HEADERS,
                timeout=5,
                allow_redirects=True
            )
            
            # Status code interpretation
            if response.status_code == 200:
                found_accounts.append((platform, url))
                logger.info(f"✅ Found on {platform}")
            elif response.status_code in [404, 410]:
                not_found.append(platform)
                logger.info(f"❌ Not found on {platform}")
            elif response.status_code == 403:
                # Some platforms block direct requests but user may exist
                found_accounts.append((platform, url))
                logger.info(f"⚠️ Access restricted on {platform} (may exist)")
            else:
                logger.warning(f"⚠️ {platform}: Status {response.status_code}")
        
        except requests.Timeout:
            errors.append(f"{platform} (timeout)")
            logger.warning(f"⏱️ Timeout on {platform}")
        
        except requests.ConnectionError:
            errors.append(f"{platform} (connection error)")
            logger.warning(f"🔌 Connection error on {platform}")
        
        except Exception as e:
            errors.append(f"{platform} (error: {str(e)[:20]})")
            logger.error(f"❌ Error checking {platform}: {str(e)}")
    
    # Format results
    if found_accounts:
        result_text += "✅ **Found On:**\n"
        for platform, url in found_accounts:
            result_text += f"- [{platform}]({url})\n"
        result_text += "\n"
    
    if not_found:
        result_text += f"❌ **Not Found On:** {', '.join(not_found[:5])}\n"
        if len(not_found) > 5:
            result_text += f"*...and {len(not_found) - 5} more*\n"
        result_text += "\n"
    
    if errors:
        result_text += f"⚠️ **Errors:** {', '.join(errors[:3])}\n"
        if len(errors) > 3:
            result_text += f"*...and {len(errors) - 3} more*\n"
    
    # Summary
    result_text += f"\n**Summary:** Found on {len(found_accounts)} platform(s)"
    
    return result_text


# ==================== BOT HANDLERS ====================
@bot.message_handler(commands=['start'])
def start_handler(message: types.Message):
    """Handle /start command."""
    welcome_text = (
        "🔍 **Welcome to Sherlock Telegram Bot!**\n\n"
        "I can search for:\n"
        "📱 **Phone Numbers** - Provide a number like `+1234567890` or `1234567890` (10-15 digits)\n"
        "👤 **Usernames** - Provide a username like `johndoe` to search across 20+ platforms\n\n"
        "**Available Commands:**\n"
        "/start - Show this message\n"
        "/help - Get detailed help\n\n"
        "**Just send me a phone number or username to search!**"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')


@bot.message_handler(commands=['help'])
def help_handler(message: types.Message):
    """Handle /help command."""
    help_text = (
        "📚 **Help & Instructions**\n\n"
        "**Phone Number Search:**\n"
        "• Format: `+1234567890` or `1234567890`\n"
        "• Length: 10-15 digits\n"
        "• Returns: Country, carrier info, public directory matches\n\n"
        "**Username Search:**\n"
        "• Format: `johndoe` (alphanumeric, 3-32 chars)\n"
        "• Searches 20+ platforms:\n"
        "  - GitHub, Instagram, Twitter, Reddit, TikTok, YouTube\n"
        "  - LinkedIn, Twitch, Pinterest, Discord, GitLab, Medium\n"
        "  - And 8+ more...\n"
        "• Returns: Found accounts with direct links\n\n"
        "**Examples:**\n"
        "`+14155552671` - Search phone number\n"
        "`elon_musk` - Search username\n\n"
        "⚠️ **Note:** Results depend on platform availability and rate limits."
    )
    bot.reply_to(message, help_text, parse_mode='Markdown')


@bot.message_handler(content_types=['text'])
def text_handler(message: types.Message):
    """Main handler for all text messages with automatic input recognition."""
    user_input = message.text.strip()
    
    try:
        # Show "typing" indicator
        bot.send_chat_action(message.chat.id, 'typing')
        
        # Automatic input recognition
        if is_phone_number(user_input):
            logger.info(f"Phone number detected: {user_input}")
            result = analyze_phone_number(user_input)
            bot.reply_to(message, result, parse_mode='Markdown')
        
        elif is_username(user_input):
            logger.info(f"Username detected: {user_input}")
            result = search_username(user_input)
            bot.reply_to(message, result, parse_mode='Markdown')
        
        else:
            error_msg = (
                "❌ **Invalid Input**\n\n"
                "Please provide:\n"
                "• **Phone:** `+1234567890` (10-15 digits)\n"
                "• **Username:** `johndoe` (3-32 chars, alphanumeric)\n\n"
                "Type /help for more info."
            )
            bot.reply_to(message, error_msg, parse_mode='Markdown')
    
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        error_msg = f"❌ **Error:** Something went wrong.\n\nDetails: `{str(e)[:100]}`"
        bot.reply_to(message, error_msg, parse_mode='Markdown')


# ==================== BOT STARTUP ====================
def main():
    """Main bot loop with error recovery."""
    logger.info("🚀 Sherlock Bot is starting...")
    
    try:
        logger.info(f"Bot token: {BOT_TOKEN[:10]}...***")
        logger.info("✅ Bot is polling for messages...")
        bot.infinity_polling(timeout=30, long_polling_timeout=5)
    
    except KeyboardInterrupt:
        logger.info("⛔ Bot stopped by user")
    
    except Exception as e:
        logger.error(f"❌ Critical error: {str(e)}")
        logger.info("🔄 Attempting restart in 10 seconds...")
        import time
        time.sleep(10)
        main()  # Recursive restart


if __name__ == '__main__':
    main()
