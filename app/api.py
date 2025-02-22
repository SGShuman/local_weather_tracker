from fastapi import APIRouter

router = APIRouter()


@router.post("/slack/weather")
async def weather_command(
    payload=None,
):
    """
    Handle /weather slash command from Slack
    Example usage: /weather
    """
    try:
        # Format response
        response = {
            "response_type": "in_channel",
            "blocks": [
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*Weather for Here*"},
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Temperature:* X°C"},
                        {"type": "mrkdwn", "text": f"*Condition:* X"},
                    ],
                },
            ],
        }

        return response

    except Exception as e:
        return {
            "response_type": "ephemeral",
            "text": f"Error fetching weather data: {str(e)}",
        }
