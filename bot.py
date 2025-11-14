import logging
import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters
import re
from dotenv import load_dotenv



load_dotenv()

# Get environment variables or use defaults for development
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8418535986:AAHaWggR8N9n8odiFqpaucQW2FudZ1ir9ds")
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
# Channel/group IDs from environment variables or defaults
source_channel = int(os.environ.get("SOURCE_CHANNEL", "-1003380827618"))
source_group = int(os.environ.get("SOURCE_GROUP", "-1003471581894"))
destination_channel = int(os.environ.get("DESTINATION_CHANNEL", "-1003394601614"))


SOURCE_CHANNEL_IDS = [-1003471581894, source_channel]
def detect_leverage(text):
    """Detects the leverage value (e.g., 50 or 100) from the signal text."""
    match = re.search(r'Leverage:\s*(?:Cross|Isolated)?\s*(\d+)x', text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None  # Unknown leverage

def detect_position(text):
    """
    Detects if the trading position is 'short' or 'long' from the signal text.
    
    Args:
    text (str): The input text containing the signal.
    
    Returns:
    str: 'short', 'long', or 'unknown' if not detected.
    """
    # Regex to find 'Direction:' followed by 'Short' or 'Long' (ignoring case and extra spaces)
    match = re.search(r'Direction:\s*(Short|Long)', text, re.IGNORECASE)
    if match:
        return match.group(1).lower()
    return 'unknown'


def get_target_multipliers(position, leverage):
    """
    Returns the list of target multipliers based on position and leverage.
    
    Args:
    position (str): 'long' or 'short'
    leverage (int): 50 or 100
    
    Returns:
    list: List of 8 multipliers for Target1 through Target8
    """
    if position == 'long' and leverage == 100:
        return [1.005, 1.007, 1.01, 1.015, 1.02, 1.025, 1.03, 1.20]
    elif position == 'short' and leverage == 100:
        return [0.995, 0.993, 0.99, 0.985, 0.98, 0.975, 0.97, 0.80]
    elif position == 'long' and leverage == 50:
        return [1.01, 1.014, 1.02, 1.03, 1.04, 1.05, 1.06, 1.40]
    elif position == 'short' and leverage == 50:
        return [0.99, 0.986, 0.98, 0.97, 0.96, 0.95, 0.94, 0.60]
    else:
        return None


def modify_text(text, fallback_entry=2.5):  # Optional fallback if no entry price found
    """
    Modifies the entry price and all target prices in the text based on position and leverage.
    Entry modifications:
    - LONG 100X: Entry * 1.001
    - SHORT 100X: Entry * 0.999
    - LONG 50X: Entry * 1.002
    - SHORT 50X: Entry * 0.998
    
    Target modifications are calculated from the modified entry price using position/leverage-specific multipliers.
    """
    position = detect_position(text)
    leverage = detect_leverage(text)
    
    # Extract entry price (assuming numeric after 'Entry:'. Use fallback if 'PRICE MODIFIED' or missing)
    entry_match = re.search(r'📊?Entry:\s*(\d+\.?\d*)', text, re.IGNORECASE)
    if entry_match:
        entry_price = float(entry_match.group(1))
    else:
        entry_price = fallback_entry
        logger.warning(f"No numeric entry price found in text, using fallback: {fallback_entry}")
    
    # Apply multiplier based on position and leverage for entry price
    if position == 'long' and leverage == 100:
        entry_multiplier = 1.001
    elif position == 'short' and leverage == 100:
        entry_multiplier = 0.999
    elif position == 'long' and leverage == 50:
        entry_multiplier = 1.002
    elif position == 'short' and leverage == 50:
        entry_multiplier = 0.998
    else:
        entry_multiplier = 1.0  # No change if unknown
        logger.warning(f"Unknown position '{position}' or leverage '{leverage}', no modification applied.")
    
    modified_entry = entry_price * entry_multiplier
    
    # Replace the entry line with the new price (handles both numeric and 'PRICE MODIFIED')
    modified_text = re.sub(
        r'📊?Entry:\s*(\d+\.?\d*|PRICE MODIFIED)', 
        f'📊Entry: {modified_entry:.6f}', 
        text, 
        flags=re.IGNORECASE
    )
    
    # Get target multipliers and modify target prices
    target_multipliers = get_target_multipliers(position, leverage)
    if target_multipliers:
        # Replace each target (Target1 through Target8)
        for i, multiplier in enumerate(target_multipliers, start=1):
            target_number = i
            new_target_price = modified_entry * multiplier
            
            # Pattern to match TargetN: followed by a number (with optional emoji or formatting)
            # This handles various formats like "Target1: 1.234", "🎯Target1: 1.234", etc.
            pattern = rf'(Target{target_number}:\s*)(\d+\.?\d*)'
            replacement = rf'\g<1>{new_target_price:.6f}'
            
            modified_text = re.sub(pattern, replacement, modified_text, flags=re.IGNORECASE)
            logger.debug(f"Modified Target{target_number}: {new_target_price:.6f} (multiplier: {multiplier})")
    
    return modified_text



async def channel_post_handler(update: Update, context) -> None:
    message = update.channel_post
    if message and message.chat_id == source_channel:
        logger.info(f"New channel post received in chat ID {message.chat_id}: {message.text}")
        
        # Modify the text (customize this logic as needed)
        new_message = modify_text(message.text )
        
        # Send the modified message to the target group
        try:
            await context.bot.send_message(chat_id=destination_channel, text=new_message)
            logger.info(f"Successfully posted modified message to group {destination_channel}")
        except Exception as e:
            logger.error(f"Failed to post to group {destination_channel}: {e}")



async def group_post_handler(update: Update, context) -> None:
    message = update.message
    if message and message.chat_id == source_group:  # Assuming you define SOURCE_GROUP_IDS similarly
        logger.info(f"New group post received in chat ID {message.chat_id}: {message.text}")
        
        # Modify the text (customize this logic as needed)
        new_message = modify_text(message.text )
 
        # Send the modified message to the target group
        try:
            await context.bot.send_message(chat_id=destination_channel, text=new_message)
            logger.info(f"Successfully posted modified message to group {destination_channel}")
        except Exception as e:
            logger.error(f"Failed to post to group {destination_channel}: {e}")


def main() -> None:
    # Replace 'BOT_TOKEN' with your actual bot token string
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Handler for channel posts
    application.add_handler(MessageHandler(filters.ChatType.CHANNEL, channel_post_handler))
    
    # Handler for group/supergroup messages (use GROUPS for both group and supergroup)
    application.add_handler(MessageHandler(filters.ChatType.GROUPS, group_post_handler))
    
    # Start polling for updates (include both types)
    application.run_polling(allowed_updates=[Update.CHANNEL_POST, Update.MESSAGE])

if __name__ == '__main__':
    main()
