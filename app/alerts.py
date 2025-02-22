import requests
from datetime import datetime
import pytz

eastern_tz = pytz.timezone('US/Eastern')
DANI = 'UT11UCRT9'
JOEL = 'USMMJAWKD'

def get_as_eastern_time(time: str):
    return datetime.fromisoformat(time.replace("Z", "+00:00")).astimezone(eastern_tz).strftime('%Y/%m/%d %H:%M:%S')


class WeatherAlerts:
    def __init__(self, SLACK_WEBHOOK_URL):
        self.webhook_url = SLACK_WEBHOOK_URL

    def send_slack(self, message: str):
        payload = {"text": message}
        response = requests.post(self.webhook_url, json=payload)
        response.raise_for_status()

    def send_daily_weather(self, weather_data: dict) -> None:
        msg = f"""
*Weather Snapshot:* ☀️

🌡️ *Temperature:* {weather_data["temperatureAvg"]:.1f}°F (Max: {weather_data["temperatureMax"]:.1f}°F, Min: {weather_data["temperatureMin"]:.1f}°F)
🌡️ *Feels Like:* {weather_data["temperatureApparentAvg"]:.1f}°F (Max: {weather_data["temperatureApparentMax"]:.1f}°F, Min: {weather_data["temperatureApparentMin"]:.1f}°F)
💧 *Humidity:* {weather_data["humidityAvg"]}% (Max: {weather_data["humidityMax"]}%, Min: {weather_data["humidityMin"]}%)
💧 *Rain Accumulation* {weather_data["rainAccumulationSum"]}
💨 *Wind:* {weather_data["windSpeedAvg"]:.1f} mph (Gusts up to {weather_data["windGustMax"]:.1f} mph)
☁️ *Cloud Cover:* {weather_data["cloudCoverAvg"]}/10 (Max: {weather_data["cloudCoverMax"]}/10)
☀️ *UV Index:* {weather_data["uvIndexAvg"]} (Max: {weather_data["uvIndexMax"]})
👀 *Visibility:* {weather_data["visibilityAvg"]:.2f} miles
🌅 *Sunrise:* {get_as_eastern_time(weather_data["sunriseTime"])}
🌇 *Sunset:* {get_as_eastern_time(weather_data["sunsetTime"])}
🌙 *Moonrise:* {get_as_eastern_time(weather_data["moonriseTime"])}
🌜 *Moonset:* {get_as_eastern_time(weather_data["moonsetTime"])}

*Additional Details:*
- Dew Point: {weather_data["dewPointAvg"]:.1f}°F
- Pressure: {weather_data["pressureSeaLevelAvg"]} inHg
- Hail Probability: {weather_data["hailProbabilityAvg"]:.1f}%

Enjoy the day! 🌤️
"""

        self.send_slack(msg)

    def send_lack_of_rain_notice(self, amt: int) -> None:
        msg = f'There have only been {amt} inches of rain in the last 7 days, get out and water Bitch. <@{DANI}>'
        self.send_slack(msg)

    def send_adequate_rain_notice(self, amt: int):
        msg = f'There has been {amt} rain in the last 7 days, no need to water my love and lord!'
        self.send_slack(msg)

    def alert_freezing(self, tmp, date):
        msg = f'It will be {tmp} F on {get_as_eastern_time(date)} <@{DANI}>'
        self.send_slack(msg)


if __name__ == "__main__":
    weather_alerts = WeatherAlerts()
    weather_alerts.send_slack("Joel loves Dani")
