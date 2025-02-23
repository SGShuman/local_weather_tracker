import requests
from datetime import datetime
import pytz

eastern_tz = pytz.timezone("US/Eastern")
DANI = "UT11UCRT9"
JOEL = "USMMJAWKD"


def get_as_eastern_time(time: str):
    return (
        datetime.fromisoformat(time.replace("Z", "+00:00"))
        .astimezone(eastern_tz)
        .strftime("%Y/%m/%d %H:%M:%S")
    )


class WeatherAlerts:
    def __init__(self, SLACK_WEBHOOK_URL):
        self.webhook_url = SLACK_WEBHOOK_URL

    def send_slack(self, message: str):
        payload = {"text": message}
        response = requests.post(self.webhook_url, json=payload)
        response.raise_for_status()

    def send_daily_weather(self, weather_data: dict) -> None:
        message = (
            "*Weather for Joel, Dani, Beebos and Mogeetsa* ☀️\n\n"
            f"🌡️ *Temperature:* {weather_data['temperatureAvg']:.1f}°F (Max: {weather_data['temperatureMax']:.1f}°F, Min: {weather_data['temperatureMin']:.1f}°F)\n"
            f"🌡️ *Feels Like:* {weather_data['temperatureApparentAvg']:.1f}°F (Max: {weather_data['temperatureApparentMax']:.1f}°F, Min: {weather_data['temperatureApparentMin']:.1f}°F)\n"
            f"💧 *Humidity:* {weather_data['humidityAvg']}% (Max: {weather_data['humidityMax']}%, Min: {weather_data['humidityMin']}%)\n"
            f"💧 *Rain Accumulation:* {weather_data['rainAccumulationSum']}\n"
            f"💨 *Wind:* {weather_data['windSpeedAvg']:.1f} mph (Gusts up to {weather_data['windGustMax']:.1f} mph)\n"
            f"☁️ *Cloud Cover:* {weather_data['cloudCoverAvg']}/10 (Max: {weather_data['cloudCoverMax']}/10)\n"
            f"☀️ *UV Index:* {weather_data['uvIndexAvg']} (Max: {weather_data['uvIndexMax']})\n"
            f"👀 *Visibility:* {weather_data['visibilityAvg']:.2f} miles\n"
            f"🌅 *Sunrise:* {get_as_eastern_time(weather_data['sunriseTime'])}\n"
            f"🌇 *Sunset:* {get_as_eastern_time(weather_data['sunsetTime'])}\n"
            f"🌙 *Moonrise:* {get_as_eastern_time(weather_data['moonriseTime'])}\n"
            f"🌜 *Moonset:* {get_as_eastern_time(weather_data['moonsetTime'])}\n"
            f"- Dew Point: {weather_data['dewPointAvg']:.1f}°F\n"
            f"- Pressure: {weather_data['pressureSeaLevelAvg']} inHg\n\n"
            "*You are smart, hardworking, beautiful, and a better cook than I give you credit for. I love you more each and every day!*"
        )
        self.send_slack(message)

    def send_lack_of_rain_notice(self, amt: int) -> None:
        m = f"There have only been {amt} inches of rain in the last 7 days, get out and water my love and lord. <@{DANI}>"
        self.send_slack(m)

    def send_adequate_rain_notice(self, amt: int):
        m = f"There has been {amt} inches of rain in the last 7 days, no need to water my love and lord!"
        self.send_slack(m)

    def alert_freezing(self, tmp, date):
        m = f"It will be {tmp} F on {get_as_eastern_time(date)} <@{DANI}>"
        self.send_slack(m)


if __name__ == "__main__":
    weather_alerts = WeatherAlerts()
    weather_alerts.send_slack("Joel loves Dani")