from datetime import datetime


def format_timestamp(value: str) -> str:
    parsed = datetime.fromisoformat(value)
    return parsed.strftime("%Y-%m-%d %H:%M:%S")
