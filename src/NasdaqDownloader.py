import requests
import re
import datetime
import time


class NasdaqDownloader:
    """ For downloading historical market data.
        Respects robots.txt
     """

    def __init__(self):
        self.request_headers = {
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'}
        self.crawl_delay: int = self._set_crawl_delay() + 1  # +1 second buffer to ensure compliance
        self.last_crawl: datetime = datetime.datetime.fromisocalendar(1970, 1, 1)

    def _set_crawl_delay(self) -> int:
        """ parses robots.txt to find the crawl delay. Uses regular expressions """
        # Downloading file
        req = requests.get('https://www.nasdaq.com/robots.txt', headers=self.request_headers)
        if req.status_code != 200:
            print('Error reading robots.txt')
            exit(1)
        content_string: str = req.text
        # Extracting data
        re.DOTALL = True  # Allows . wildcard to actually match all characters
        regex = re.compile('.*User-agent: \\*\\nCrawl-delay: ([0-9]*)')
        match_list: list = regex.findall(content_string)[0]
        if not match_list:
            print('Did not find a crawl delay in robots.txt')
            exit(1)
        delay: int = int(match_list)
        return delay

    def pull_all_symbols(self):
        """ Pulls complete list of nasdaq stock symbols from nasdaq.com """
        self._enforce_crawl_delay()
        dl_url: str = 'https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=25&offset=0&download=true'
        req = requests.get(dl_url, headers=self.request_headers)
        self.last_crawl = datetime.datetime.now()
        if req.status_code != 200:
            return -1, {'error_message': req.text}
        return 0, {'content': req.json()}

    def pull_symbol_data(self,
                         stock_symbol: str,
                         day_of_month: str,
                         month: str) -> tuple[int, dict]:
        """ Pulls historic data for a given stock symbol going back 10 years.
        """
        self._enforce_crawl_delay()
        # Pulling data
        # API is inconsistent though. Some require using a day prior, others give errors when doing so..
        api_url: str = f'https://api.nasdaq.com/api/quote/{stock_symbol}/historical?assetclass=stocks&fromdate=' \
                       f'2011-{month}-{day_of_month}&limit=9999&todate=2021-{month}-{day_of_month}'
        req = requests.get(api_url, headers=self.request_headers)
        self.last_crawl = datetime.datetime.now()
        if req.status_code != 200:
            return -1, {'error_message': req}
        return 0, {'content': req.json()}

    def _enforce_crawl_delay(self) -> None:
        """ Called by pull_data to ensure program adheres to robots.txt
            Suspends program for remaining time until next authorized crawl activity
        """
        time_delta = datetime.datetime.now() - self.last_crawl  # Time since last request
        td_seconds = time_delta.total_seconds()
        if self.crawl_delay > td_seconds:
            # Not enough time has yet elapsed since the last request..
            remaining_time = self.crawl_delay - td_seconds
            print(f'Need to wait another {remaining_time} seconds for the crawl delay..', datetime.datetime.now())
            time.sleep(remaining_time)

