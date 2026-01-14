from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

def epoch_to_datetime(epoch: int) -> datetime:
    if epoch > 1e12:  # milliseconds
        epoch /= 1000
    return datetime.fromtimestamp(epoch, tz=timezone.utc).astimezone(IST)
