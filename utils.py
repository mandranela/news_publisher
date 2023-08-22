import json
import os
from datetime import datetime, timedelta


def parse_time_string(time_str: str) -> datetime:
    try:
        time_str = time_str.strip()
        num, unit = time_str.split(' ')[:2]
        if unit.startswith('мин'):
            delta = timedelta(minutes=int(num))
        elif unit.startswith('час'):
            delta = timedelta(hours=int(num))
        else:
            delta = timedelta(days=int(num))
    except ValueError:
        delta = timedelta(days=0, hours=0, minutes=0, seconds=1)

    return datetime.now() - delta
