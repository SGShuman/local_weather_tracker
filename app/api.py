from fastapi import APIRouter, Response, Depends
from scheduled_tasks import daily_weather, check_rain
from weather import WeatherService
from database import WeatherDatabase
from alerts import WeatherAlerts
from services import get_weather_service, get_alerts_service, get_database_service

router = APIRouter()


@router.post("/slack/weather")
async def weather_command(
    weather_service: WeatherService = Depends(get_weather_service),
    alerts: WeatherAlerts = Depends(get_alerts_service),
    database: WeatherDatabase = Depends(get_database_service),
):
    """
    Handle /weather slash command from Slack
    """
    daily_weather(weather_service, alerts, database)
    try:
        return Response(status_code=200)

    except Exception as e:
        return {
            "response_type": "ephemeral",
            "text": f"Error fetching weather data: {str(e)}",
        }

@router.post("/slack/check_rain")
async def check_rain_command(
    alerts: WeatherAlerts = Depends(get_alerts_service),
    database: WeatherDatabase = Depends(get_database_service),
):
    """
    Handle /weather slash command from Slack
    """
    check_rain(alerts, database)
    try:
        return Response(status_code=200)

    except Exception as e:
        return {
            "response_type": "ephemeral",
            "text": f"Error checking for rain: {str(e)}",
        }
