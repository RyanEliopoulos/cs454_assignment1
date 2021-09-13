"""
    Requires Python 3.7+ due to the type hinting for tuples.
"""
from DBInterface import DBInterface
from NasdaqDownloader import NasdaqDownloader
from RedditCommunicator import RedditCommunicator
from RedditParser import RedditParser
import misc


class Controller:

    def __init__(self, db_path: str):
        self.db_interface = DBInterface(db_path)
        self.nd_downloader = NasdaqDownloader()
        self.r_communicator = RedditCommunicator()

    def build_symbol_list(self) -> None:
        """ Retrieves the list of stock symbols from nasdaq.com and updates the database.
        """
        # Downloading data
        ret = self.nd_downloader.pull_all_symbols()
        if ret[0] != 0:
            print(f'Encountered error downloading data from nasdaq: {ret}')
        content: dict = ret[1]['content']
        data: dict = content['data']
        rows: dict = data['rows']
        # Building list of stock symbols
        prepared_symbols: list = []
        # Excising stock class indicators (symbols appended with a string beginning with ^)
        for row in rows:
            symbol: str = row['symbol']
            trunced_symbol: str = symbol.split('^')[0]
            prepared_symbols.append(trunced_symbol)
        # Inserting into the database. Key constraints prevent any dups
        for sym in prepared_symbols:
            ret = self.db_interface.insert_symbol(sym)
            if ret[0] != 0:
                print(f'Error inserting {sym}: {ret}')
        # Now pruning the values that were erroneously added
        # Added after the fact so its sloppy.
        self.prune_invalid_symbols()

    def prune_invalid_symbols(self):
        """ Some stock symbols don't have a base value not followed by a caret denoting some special class or
            status for the stock.  The initial assumption was one would exist for every symbol, so truncating
            the caret and inserting the base symbol would be fine. Now there are invalid symbols in the table.

            Checks values in the DB against the raw values from nasdaq.com
        """
        ret = self.nd_downloader.pull_all_symbols()
        if ret[0] != 0:
            print(f'Encountered error downloading data from nasdaq: {ret}')
        # Unpacking values
        content: dict = ret[1]['content']
        data: dict = content['data']
        rows: dict = data['rows']
        # Building hash of all returned values
        raw_symbols: dict = {}
        for row in rows:
            symbol: str = row['symbol']
            raw_symbols[symbol] = 1
        # Pulling values from db
        ret = self.db_interface.symbol_list()
        if ret[0] != 0:
            print(f'Error pulling symbols from db: {ret}')
        stored_list: list = ret[1]['content']
        for stored_symbol in stored_list:
            if stored_symbol not in raw_symbols:
                ret = self.db_interface.prune_symbol(stored_symbol)
                if ret[0] != 0:
                    print(f'Error pruning symbol {stored_symbol}')
                else:
                    print(f'Sucessfully deleted symbol {stored_symbol} from the db.')

    def populate_historical_data(self, count: int = 20) -> tuple[int, dict]:
        """ Pulls a list of stock symbols still requiring historical data and begins updating.
            Count caps the number of symbols that will be updated. This is because
            the crawl delay is 30 seconds and the # of symbols is in the thousands.
            Best done a little at a time.
        """
        ret = self.db_interface.naked_symbols()
        if ret[0] != 0:
            return ret
        remaining_symbols: list = ret[1]['content']
        # Getting day/month strings for API calls
        # API is inconsistent. Some symbols require today values, others yesterday values.
        today, yesterday, month, yestermonth = misc.api_days()
        # Pulling data from nasdaq for each symbol
        for symbol in remaining_symbols:
            pull_ret = self.nd_downloader.pull_symbol_data(symbol, today, month)
            print(f'Querying data for {symbol}')
            if pull_ret[0] != 0:
                print(f'Error pulling historical data for {symbol}: {ret}')
                continue
            try:
                row_data: list = pull_ret[1]['content']['data']['tradesTable']['rows']
            except TypeError:
                print(""" Today didn't work for the API call. Yesterday probably will """)
                pull_ret = self.nd_downloader.pull_symbol_data(symbol, yesterday, yestermonth)
            try:
                row_data: list = pull_ret[1]['content']['data']['tradesTable']['rows']
            except TypeError:
                print('Both today and yesterday values failed the API call. Updating historical data')
                exit(1)
            # Updating database
            print(f'loading data for {symbol}')
            for row in row_data:
                # Converting MM/DD/YYYY to unix timestamp
                date_timestamp: float = misc.historical_date_fix(row['date'])
                # Removing first character ($) from values
                open: float = float(row['open'][1:])
                close: float = float(row['close'][1:])
                high: float = float(row['high'][1:])
                low: float = float(row['low'][1:])
                # Removing commas
                c_free: str = row['volume'].split(',')
                try:
                    volume: int = int(''.join(c_free))
                except ValueError:  # Means an 'N/A' was encountered.
                    volume: int = 0
                ret = self.db_interface.populate_data(symbol
                                                      , date_timestamp
                                                      , open
                                                      , close
                                                      , high
                                                      , low
                                                      , volume)
                if ret[0] != 0:
                    print(f'Error loading data for {symbol}: {ret}')
            # Intermittent breaks encouranged consdering the # of symbols
            # and the crawl delay.
            count -= 1
            if count == 0:
                break

    def crawl_wsb(self, start: float, end: float) -> None:
        """ Crawls reddit posts between the given start and end timestamps """
        # Pulling relevant posts from Reddit
        ret = self.r_communicator.crawl_posts(start, end)
        if ret[0] != 0:
            print(ret)
        posts = ret[1]['content']
        # Retrieving the list of stock symbols
        ret = self.db_interface.symbol_list()
        if ret[0] != 0:
            print(f'Error querying db for symobls: {ret}')
            exit(1)
        symbol_list: list = ret[1]['content']
        # Parsing and filtering posts
        rp: RedditParser = RedditParser(posts, symbol_list)
        matching_posts: list[dict] = rp.parse()
        # Inserting into database
        print('Updating database with posts')
        for post in matching_posts:
            ret = self.db_interface.insert_post(post)
            if ret[0] != 0:
                print(f'Error inserting post into database: {ret}')
