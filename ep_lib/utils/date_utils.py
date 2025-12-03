from datetime import datetime, timezone, timedelta

def get_now_utc() -> str:
    """
    Returns the current timezone-aware UTC datetime as an ISO string.
    Use this instead of datetime.now() to ensure consistency across servers.
    """
    return datetime.now(timezone.utc).isoformat()


def get_past_date_str(hours: int = 24, fmt: str = "%Y-%m-%d") -> str:
    """
    Returns the date string for X hours ago. 
    
    Args:
        hours (int): The number of hours to go back (default: 24).
        fmt (str): The format string for the date (default: "%Y-%m-%d").
    """
    return (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime(fmt)


def get_start_at_midnight(days=0, hours=0) -> str:
    """
    Returns the datetime at midnight (00:00:00) of the day shifted
    by a certain number of days or hours from now as an ISO string.

    days: int → negative means past days, positive means future days
    hours: int → shift by hours before computing midnight
    """
    now = datetime.now(timezone.utc)

    # Apply day/hour shift
    shifted = now + timedelta(days=days, hours=hours)

    # Return midnight of that date
    return shifted.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()