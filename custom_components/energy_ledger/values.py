from __future__ import annotations

from datetime import datetime


def timestamp_value(value):
    """Convert an API timestamp to the aware datetime required by Home Assistant."""
    if value is None or isinstance(value, datetime):
        result = value
    elif isinstance(value, str):
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    else:
        raise ValueError("timestamp must be an ISO string or datetime")
    if result is not None and result.tzinfo is None:
        raise ValueError("timestamp must include a timezone")
    return result
