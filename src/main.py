"""
    May not work on new year's day due to 'yesterday' calculation method.
"""

import misc
import Controller
import datetime


if __name__ == '__main__':
    args = misc.argparser()
    cont = Controller.Controller('testing.db')
    if args.seed:
        cont.seed()
    if args.symbols:
        cont.build_symbol_list()
    if args.prune:
        cont.prune_invalid_symbols()
    if args.historical:
        cont.populate_historical_data()
    if args.wsb:
        end_timestamp = datetime.datetime.now().timestamp()
        start_timestamp = end_timestamp - (60 * 60 * 24 * 7)  # 7 days back in time in seconds
        cont.crawl_wsb(start_timestamp, end_timestamp)


