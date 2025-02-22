import requests
from config import Config

class WeatherService:
    def __init__(self, URL, KEY):
        self.api_url = URL
        self.api_key = KEY
        self.params = {
            "location": "35.60524368286133, -82.50408935546875",
            "apikey": self.api_key,
            "units": "imperial",
        }
        self.headers = {
            "accept": "application/json",
            "Accept-Encoding": "gzip",
            "content-type": "application/json",
        }

    def fetch_realtime_weather_data(self) -> dict[str, dict]:
        url = f"{self.api_url}realtime"
        response = requests.get(url, params=self.params, headers=self.headers)
        response.raise_for_status()
        data = response.json()["data"]["values"]
        return data

    def fetch_last_24hrs_weather_data(self) -> dict:
        """Gets history of what happened in the last 24 hours"""
        url = f"{self.api_url}history/recent"
        params = self.params
        params["timesteps"] = ["1d"]
        response = requests.get(url, params=params, headers=self.headers)
        response.raise_for_status()
        data = response.json()["timelines"]["daily"][0]['values']
        data['weather_date'] = response.json()["timelines"]["daily"][0]['time']
        return data

    def fetch_forecast_weather_data(self) -> list[dict]:
        """Returns forecast for next five days"""
        url = f"{self.api_url}forecast"
        params = self.params
        params["timesteps"] = ["1d"]
        response = requests.get(url, params=params, headers=self.headers)
        response.raise_for_status()
        data = response.json()["timelines"]["daily"]
        return data


if __name__ == "__main__":
    config = Config()
    weather_service = WeatherService(config.WEATHER_API_URL, config.WEATHER_API_KEY)
    data = weather_service.fetch_forecast_weather_data()
    print(data)
