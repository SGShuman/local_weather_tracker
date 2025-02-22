import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

class Config:
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
    SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "your_default_webhook_url")
    WEATHER_API_URL = "https://api.tomorrow.io/v4/weather/"
