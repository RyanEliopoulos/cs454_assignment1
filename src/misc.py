import datetime


def historical_date_fix(date_string: str) -> float:
    """ expecting 'MM/DD/YYYY' """
    date_pieces = date_string.split('/')
    month: int = int(date_pieces[0])
    day: int = int(date_pieces[1])
    year: int = int(date_pieces[2])
    return float(datetime.datetime(year, month, day).timestamp())


def api_days() -> tuple[str, str, str, str]:
    """ Returns
            day of the month: DD
            yesterday of the month: DD
            month: MM
            yestermonth: MM
    """
    # Today solved
    now = datetime.datetime.now()
    day_of_month = now.strftime('%d')
    month = now.strftime('%m')

    # How to get previous day and month?
    yesterday_timestamp = now.timestamp() - 86400  # 1 day ago
    yesterday = datetime.datetime.fromtimestamp(yesterday_timestamp)
    yesterday_day = yesterday.strftime('%d')
    yester_month = yesterday.strftime('%m')
    return day_of_month, yesterday_day, month, yester_month





