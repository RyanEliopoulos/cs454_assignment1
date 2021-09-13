import datetime
import argparse


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


def argparser() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', action='store_true', help='Initialize/reset the database')
    parser.add_argument('--symbols', action='store_true', help='Populate stock symbols from nasdaq.com')
    parser.add_argument('--historical', action='store_true',
                        help='Load historical data for the symbols currently in the database')
    parser.add_argument('--prune', action='store_true', help='Removes')
    parser.add_argument('--wsb', action='store_true', help='Crawl the last 7 days of WSB posts')
    return parser.parse_args()



