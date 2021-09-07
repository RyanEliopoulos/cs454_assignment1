"""

    Responsible for interfacing with the Reddit API

"""

import json
import requests
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

    def request_of_somesort(self):
        """ Need to decide on rules for scrapping """
        # Checking freshness of the access token
        current_time: datetime.datetime = datetime.datetime.now()
        time_delta: datetime.timedelta = current_time - self.token_timestamp
        elapsed_seconds: float = time_delta.total_seconds()
        if elapsed_seconds >= 3000:
            self.get_token()

        headers = {
            'User-Agent': 'ham/.01 by SPQRMP',
            'Authorization': f'Bearer {self.access_token}'
        }
        latest_ret = requests.get(self.content_base + 'wallstreetbets/hot', headers=headers)
        if latest_ret.status_code != 200:
            print('Error getting content')
            print(latest_ret.text)
            exit(1)
        ret_dict = latest_ret.json()
        data = ret_dict['data']
        posts: list = data['children']  # This itself is now made up of a list of listings?
        for post in posts:
            if post['data']['author_fullname'] == 't2_7j95264g':
                for key in post['data'].keys():
                    print(key, post['data'][key])
                # print(post)
            # print(post)

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


