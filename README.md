<h2> Topic </h2>

The program scrapes the wallstreetbets subreddit, parses posts looking for stock symbols, and 
documents which posts contain which symbols. Paired with historical pricing data, this data set will allow analysis 
of any predictive power wallstreetbets may have.

<h2>Required credentials</h2>

This program scrapes nasdaq.com and uses the reddit api.  Reddit requires app registration to obtain access keys plus
a register user account that is considered the acting entity. This program expects a config.json file in the /src 
directory structured as: {'username': <>, 'password': <>, 'client_id': <>, 'secret': <>}


<h3> Crawl Rates </h3>

Nasdaq.com has a 30 second crawl delay. With about ~7500 stock symbols, getting historical data for everything takes
some time. --historical gathers data on 120 stock symbols before terminating.  You can build a bash script if you want
to busy your PC for days.

Reddit.com is much more permissive. Takes maybe 60 seconds to download and process the most recent posts to wsb.

<h3> Command line arguments: </h3>

    --seed: Initializes the SQLite database. Will reset an existing database

    --symbols: Downloads and insert the stock symbol list from nasdaq.com

    --historical: Begins downloading 10 years of historical data for all stock symbols currently without.

    --prune: Downloads a fresh list of stock symbols, eliminating local symbols no longer present. Historical data and
             wsb posts are preserved.

    --wsb: Scrapes the most recent 1000 posts on r/wallstreetbets or all posts in the last 7 days, whichever is smaller.


<h3>Misc</h3>

    --Stock symbols seem to be added/removed with some regularly, necessitating the --prune option, otherwise --historical 
        will fail. 
<br>
Because day and month values are required by the nasdaq.com API there is some funkyness with the program. Server 
timezone isn't clear, though I would guess it is east coast time. As such, the program may not work between 9pm-12am.

There's also a weird bug in the API where we have to say today is yesterday.  The fix for that probably makes this 
program unusuable on new year's day.

e think this program will require python 3.7+ thanks to the type hinting, specifically my use of 'tuple[int, dict]'.
replacing the tuple keyword with the imported typehint class will drop requirements down at least to 3.6.


