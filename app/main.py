from contextlib import asynccontextmanager

import uvicorn
from alerts import WeatherAlerts
from api import router
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import Config
from database import WeatherDatabase
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scheduled_tasks import daily_weather, check_freezing, check_rain
from weather import WeatherService

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for the FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup
    config = Config()

    # Initialize services
    weather_service = WeatherService(config.WEATHER_API_URL, config.WEATHER_API_KEY)
    slack_service = WeatherAlerts(config.SLACK_WEBHOOK_URL)
    database = WeatherDatabase()

    scheduler.add_job(
        daily_weather,
        "cron",
        hour=8,  # Run at 8 AM
        minute=0,
        kwargs={
            "weather_service": weather_service,
            "slack_service": slack_service,
            "database": database,
        },
    )
    scheduler.add_job(
        check_freezing,
        "cron",
        hour=15,  # Run at 8 AM
        minute=0,
        kwargs={
            "weather_service": weather_service,
            "slack_service": slack_service,
        },
    )
    scheduler.add_job(
        check_rain,
        "cron",
        hour=8,  # Run at 8 AM
        minute=0,
        kwargs={
            "slack_service": slack_service,
            "database": database,
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

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(router, tags=["slack"])
    return app


# Create the application instance
app = create_application()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
