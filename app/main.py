from contextlib import asynccontextmanager
from datetime import datetime

import pytz
import uvicorn
from api import router
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import WeatherDatabase
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from scheduled_tasks import check_freezing, check_rain, daily_weather
from services import (
    get_alerts_service,
    get_config,
    get_database_service,
    get_weather_service,
)
from weather import WeatherService

scheduler = AsyncIOScheduler()
templates = Jinja2Templates(directory="templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for the FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup
    config = get_config()
    weather_service = get_weather_service(config)
    slack_service = get_alerts_service(config)
    database = get_database_service()

    scheduler.add_job(
        daily_weather,
        "cron",
        hour=4,  # Run at 8 AM
        minute=53,
        kwargs={
            "weather_service": weather_service,
            "weather_alert": slack_service,
            "database": database,
            "send_on":''
        },
    )
    scheduler.add_job(
        check_freezing,
        "cron",
        hour=15,  # Run at 3 PM
        minute=0,
        kwargs={
            "weather_service": weather_service,
            "weather_alert": slack_service,
            'send_on':''
        },
    )
    scheduler.add_job(
        check_rain,
        "cron",
        hour=8,  # Run at 8 AM
        minute=5,
        kwargs={
            "weather_alert": slack_service,
            "database": database,
            'send_on':''
        },
    )

    scheduler.start()
    yield  # FastAPI running
    scheduler.shutdown()

    # Shutdown


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application
    """
    app = FastAPI(
        title="Weather Slackbot",
        description="A Slack bot that provides weather information and daily updates",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router, tags=["slack"])
    app.mount("/static", StaticFiles(directory="static"), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def read_root(
        request: Request, weather_service: WeatherService = Depends(get_weather_service)
    ):
        """Render the index.html page"""
        weather_data = weather_service.fetch_realtime_weather_data()
        data = {str(k): v for k, v in weather_data.items()}
        # Convert the weather_date to Eastern time
        utc_dt = datetime.strptime(str(data["weather_date"]), "%Y-%m-%dT%H:%M:%SZ")
        eastern = pytz.timezone("America/New_York")
        eastern_dt = utc_dt.replace(tzinfo=pytz.UTC).astimezone(eastern)
        data["weather_date"] = eastern_dt.strftime("%Y-%m-%d %I:%M %p ET")
        return templates.TemplateResponse(
            "index.html", {"request": request, "weather": data}
        )

    @app.get("/weather", response_class=HTMLResponse)
    async def read_historic(
        request: Request, database: WeatherDatabase = Depends(get_database_service)
    ):
        """Render the index_historic.html page"""
        weather_data = database.get_latest_weather()
        data = {
            str(k): str(v) for k, v in weather_data.to_dict(orient="records")[0].items()
        }
        return templates.TemplateResponse(
            "index_historic.html", {"request": request, "weather": data}
        )

    @app.get("/api/weather")
    async def get_weather(
        weather_service: WeatherService = Depends(get_weather_service),
    ):
        """Return weather data as JSON"""
        weather_data = weather_service.fetch_realtime_weather_data()
        return {str(k): v for k, v in weather_data.items()}

    @app.get("/api/weather_historic")
    async def get_weather_historic(
        database: WeatherDatabase = Depends(get_database_service),
    ):
        """Return historic weather data as JSON"""
        weather_data = database.get_latest_weather()
        return {
            str(k): str(v) for k, v in weather_data.to_dict(orient="records")[0].items()
        }

    return app


# Create the application instance
app = create_application()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
