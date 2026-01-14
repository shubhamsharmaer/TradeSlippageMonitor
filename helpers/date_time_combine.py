from datetime import datetime, date, time

def combine_date_and_time(trade_date: date, time_str: str) -> datetime:
    """
    Combine date + HH:MM:SS into datetime
    """
    t = datetime.strptime(time_str, "%H:%M:%S").time()
    return datetime.combine(trade_date, t)
