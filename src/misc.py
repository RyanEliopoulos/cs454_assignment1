import datetime


def historical_date_fix(date_string: str) -> float:
    """ expecting 'MM/DD/YYYY' """
    date_pieces = date_string.split('/')
    month: int = int(date_pieces[0])
    day: int = int(date_pieces[1])
    year: int = int(date_pieces[2])
    return float(datetime.datetime(year, month, day).timestamp())
