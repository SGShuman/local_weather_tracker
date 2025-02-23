# services.py
from functools import lru_cache
from fastapi import Depends
from weather import WeatherService
from database import WeatherDatabase
from alerts import WeatherAlerts
from config import Config

@lru_cache()
def get_config():
    return Config()

def get_weather_service(config: Config = Depends(get_config)):
    return WeatherService(config.WEATHER_API_URL, config.WEATHER_API_KEY)

def get_alerts_service(config: Config = Depends(get_config)):
    return WeatherAlerts(config.SLACK_WEBHOOK_URL)

def get_database_service():
    return WeatherDatabase()