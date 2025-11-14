# Telegram Message Modifier Bot

A Telegram bot that listens to messages in specific channels/groups and forwards modified versions to a destination channel.

## Requirements

- Python 3.8+
- python-telegram-bot library (v13.15)
- python-dotenv (v1.0.0)

## Deployment on Render.com

### Prerequisites

1. Create a Git repository (GitHub, GitLab, or Bitbucket) and push this code to it.
2. Sign up for a [Render.com](https://render.com/) account if you don't already have one.

### Steps to Deploy

1. Log in to your Render.com account.
2. Click on "New" and select "Background Worker" from the dropdown menu.
3. Connect your Git repository where you pushed the bot code.
4. Fill in the following details:
   - Name: `telegram-message-modifier` (or any name you prefer)
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python bot.py` (already specified in the Procfile)
5. Add the following environment variables:
   - `BOT_TOKEN`: Your Telegram bot token
   - `SOURCE_CHANNEL`: Your source channel ID (e.g., -1003380827618)
   - `SOURCE_GROUP`: Your source group ID (e.g., -1003471581894)
   - `DESTINATION_CHANNEL`: Your destination channel ID (e.g., -1003394601614)
6. Click "Create Background Worker"

### Monitoring

You can monitor your bot's logs through the Render.com dashboard. If your bot encounters any issues, you can review the logs to troubleshoot.
 