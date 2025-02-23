from contextlib import contextmanager

import duckdb
from pandas import DataFrame
from sql.create_weather import create_weather_query


class WeatherDatabase:
    DB_PATH = "weather_data.db"

    def __init__(self):
        self.init_db()

    @contextmanager
    def get_conn(self):
        """Context manager for database connections to ensure proper cleanup."""
        conn = duckdb.connect(self.DB_PATH)
        try:
            yield conn
        finally:
            conn.close()

    def init_db(self):
        with self.get_conn() as conn:
            conn.execute(create_weather_query)
        

    def process_daily_weather(self, data: dict) -> None:
        columns, values = [], []
        for k, v in data.items():
            columns.append(k)
            values.append(v)
        placeholders = ', '.join(['?' for _ in columns])  # Create placeholders
        sql = f"INSERT INTO weather ({', '.join(columns)}) VALUES ({placeholders})"
        with self.get_conn() as conn:
            conn.execute(sql, values)

    def get_latest_weather(self) -> DataFrame:
        with self.get_conn() as conn:
            return conn.execute(
                "SELECT * FROM weather ORDER BY weather_date DESC LIMIT 1"
            ).fetchdf()

    def check_if_rain(self):
        with self.get_conn() as conn:
            result = conn.execute(
                "SELECT SUM(rainAccumulationSum) as rain_inches FROM weather WHERE weather_date >= CURRENT_DATE - INTERVAL '7' DAY"
            ).fetchone()
        return result[0]


if __name__ == "__main__":
    weather_db = WeatherDatabase()
    df = weather_db.get_latest_weather()
    print(df)
