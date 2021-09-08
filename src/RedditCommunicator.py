"""

    Responsible for interfacing with the Reddit API

"""

import json
import requests
import time
import datetime
from requests.auth import HTTPBasicAuth


class RedditCommunicator:

    """ Access token is valid for 60 minutes. """
    token_endpoint: str = 'https://www.reddit.com/api/v1/access_token'
    content_base: str = 'https://oauth.reddit.com/r/'

    def __init__(self):
        self.access_token: str = ''  # Updated in get_token
        self.token_time: datetime.datetime   # Creation time. Updated in get_token
        self.get_token()
        self.rlimit_remaining: int = 600  # Remaining API calls allowed for given unit of time
        self.rlimit_reset: int = 0  # Duration until rate limit is reset

    def get_token(self) -> None:
        """ Responsible for getting an access token for API calls """
        with open('config.json', 'r') as config_file:
            json_rep = json.load(config_file)
            username = json_rep['username']
            password = json_rep['password']
            client_id = json_rep['client_id']
            secret = json_rep['secret']
        # Building request
        data: dict = {
            'grant_type': 'password',
            'username': username,
            'password': password

        }
        user_agent: str = f'ham/.01 by {username}'  # Reddit API requires custom user agent
        headers: dict = {
            'User-Agent': user_agent
        }
        ret = requests.post(self.token_endpoint,
                            data=data,
                            auth=HTTPBasicAuth(client_id, secret),
                            headers=headers)
        if ret.status_code != 200:
            print('Error retrieving access token')
            print(ret.text)
            exit(1)
        # Updating token variables
        ret_json: dict = ret.json()
        self.token_timestamp = datetime.datetime.now()
        self.access_token = ret_json['access_token']

    def check_token(self):
        """ To be called before each API request.
            Ensures valid access token will be used.
        """
        # Checking freshness of the access token
        current_time: datetime.datetime = datetime.datetime.now()
        time_delta: datetime.timedelta = current_time - self.token_timestamp
        elapsed_seconds: float = time_delta.total_seconds()
        if elapsed_seconds >= 3000:
            self.get_token()

    def crawl_posts(self, start: float, end: float):
        """ crawls postings from "new" between the given dates.
            start and end are unix timestamps
        """
        self.check_token()
        # Pulling newest post
        headers = {
            'User-Agent': 'ham/.01 by SPQRMP',
            'Authorization': f'Bearer {self.access_token}'
        }
        # latest_ret = requests.get(self.content_base + 'wallstreetbets/new', headers=headers)
        latest_ret = self.crawl_request(headers=headers)
        if latest_ret.status_code != 200:
            print(f'Error getting content from wsb {latest_ret.text}')
            exit(1)
        ret_dict = latest_ret.json()
        data: dict = ret_dict['data']
        raw_posts: list = data['children']  # 'Listings' indexed newest at 0.
        post_date: float = raw_posts[0]['data']['created_utc']  # unix timestamp
        # Iterating through posts now
        desired_posts: list = []
        while True:
            for post in raw_posts:
                if post_date < start:  # Beyond earliest desired time. Crawling complete.
                    break
                if post_date > end:  # Beyond latest desired time. Moving to next post
                    continue
                desired_posts.append(post)
            # Checking fnx exit condition
            if post_date < start:
               break
            # Preparing next GET request
            last_post: dict = raw_posts[-1]
            post_name: str = last_post['data']['name']  # point of reference for the reddit API
            params = {
                'after': post_name
            }
            # Retrieving next batch of posts
            self.check_token()
            ret = self.crawl_request(headers=headers, params=params)
            if ret.status_code != 200:
                print(f'Error downloading wsb posts: {ret.text}')
                exit(1)
            # Beginning cycle anew
            data = ret.json()['data']
            raw_posts = data['children']
            post_date: float = raw_posts[0]['data']['created_utc']  # unix timestamp
        return 0, {'content': desired_posts}

    def crawl_request(self,
                      headers: dict = {},
                      params: dict = {},
                      ) -> requests.Response:
        """ returns the output from requests.get.
            Separate fnx in order to simplify rate limit adherence.
        """
        # Checking rate limit situation
        if self.rlimit_remaining == 0:
            time.sleep(self.rlimit_reset+2)
        ret = requests.get(self.content_base + 'wallstreetbets/new',
                           headers=headers,
                           params=params)
        self.rlimit_remaining = int(float(ret.headers['x-ratelimit-remaining']))  # str to float to int
        self.rlimit_reset = ret.headers['x-ratelimit-reset']
        return ret

    def manual(self):
        names = 't3_piyhzv'
        headers = {
            'User-Agent': 'ham/.01 by SPQRMP',
            'Authorization': f'Bearer {self.access_token}'
        }
        ret = requests.get(self.content_base + 'by_id' + names,
                           headers=headers)
        if ret.status_code != 200:
            print('Manual error')
            exit(1)
        print(ret.json())


