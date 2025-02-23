from datetime import datetime

import pytz
from alerts import WeatherAlerts
from config import Config
from database import WeatherDatabase
from weather import WeatherService

eastern_tz = pytz.timezone("US/Eastern")


def get_day_of_week_eastern():
    return datetime.now(eastern_tz).strftime("%A")


DOW = get_day_of_week_eastern()


def daily_weather(
    weather_service: WeatherService,
    weather_alert: WeatherAlerts,
    database: WeatherDatabase,
    send_on: str = None,
) -> None:
    data = weather_service.fetch_last_24hrs_weather_data()
    database.process_daily_weather(data)
    if send_on and send_on != DOW:
        return
    weather_alert.send_daily_weather(data)


def check_rain(
    weather_alert: WeatherAlerts,
    database: WeatherDatabase,
    send_on: str = None,
) -> None:
    if send_on and send_on != DOW:
        return
    rain_inches = database.check_if_rain()
    if rain_inches < 1:
        weather_alert.send_lack_of_rain_notice(rain_inches)
    else:
        weather_alert.send_adequate_rain_notice()


def check_freezing(
    weather_service: WeatherService,
    weather_alert: WeatherAlerts,
    send_on: str = None,
) -> None:
    if send_on and send_on != DOW:
        return
    data = weather_service.fetch_forecast_weather_data()
    for day in data[1:]:  # skip today
        low = day["values"]["temperatureMin"]
        if low <= 32:
            weather_alert.alert_freezing(low, day["time"])
            return


if __name__ == "__main__":
    # Startup
    config = Config()

    # Initialize services
    weather_service = WeatherService(config.WEATHER_API_URL, config.WEATHER_API_KEY)
    slack_service = WeatherAlerts(config.SLACK_WEBHOOK_URL)
    database = WeatherDatabase()
    # daily_weather(weather_service, slack_service, database)
    # check_rain(slack_service, database)
    check_freezing(weather_service, slack_service)
