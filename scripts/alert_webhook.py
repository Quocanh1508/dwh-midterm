"""
alert_webhook.py
================
Sends a success or failure notification to a Discord or Slack Webhook based
on the status of the GitHub Actions pipeline.

Usage:
  python scripts/alert_webhook.py success "CI Pipeline passed all tests!"
  python scripts/alert_webhook.py failure "CD Pipeline failed. Check logs."

Requires either `DISCORD_WEBHOOK_URL` or `SLACK_WEBHOOK_URL` in environment.
"""

import sys
import os
import requests
import pathlib
from dotenv import load_dotenv

def send_discord_webhook(url: str, status: str, message: str):
    color = 3066993 if status == "success" else 15158332 # Green vs Red
    
    payload = {
        "embeds": [
            {
                "title": f"DWH Pipeline: {status.upper()}",
                "description": message,
                "color": color
            }
        ]
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"✅ Alert sent to Discord.")
    except Exception as e:
        print(f"❌ Failed to send Discord alert: {e}")

def send_slack_webhook(url: str, status: str, message: str):
    emoji = "✅" if status == "success" else "❌"
    
    payload = {
        "text": f"{emoji} *DWH Pipeline: {status.upper()}*\n{message}"
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"✅ Alert sent to Slack.")
    except Exception as e:
        print(f"❌ Failed to send Slack alert: {e}")

def main():
    if len(sys.argv) < 3:
        print("Usage: python alert_webhook.py <success|failure> <message>")
        sys.exit(1)
        
    status = sys.argv[1].lower()
    message = sys.argv[2]
    
    # Check for Discord/Slack URLs
    root_dir = pathlib.Path(__file__).parent.parent
    load_dotenv(root_dir / ".env")
    
    discord_url = os.environ.get("DISCORD_WEBHOOK_URL")
    slack_url = os.environ.get("SLACK_WEBHOOK_URL")
    
    if not discord_url and not slack_url:
        print("⚠️ No Webhook URLs found in environment (.env). Skipping alerts.")
        sys.exit(0)
        
    if discord_url:
        send_discord_webhook(discord_url, status, message)
    
    if slack_url:
        send_slack_webhook(slack_url, status, message)

if __name__ == "__main__":
    main()
