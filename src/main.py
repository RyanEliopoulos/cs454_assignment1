import requests
from requests.auth import HTTPBasicAuth
import json

import Controller

# with open('config.json', 'r') as config_file:
#     json_rep = json.load(config_file)
#     username = json_rep['username']
#     password = json_rep['password']
#     client_id = json_rep['client_id']
#     secret = json_rep['secret']
#
# print(username, password, client_id, secret)
#
# access_token = '53781142054-m88rv79ElvThKEHpk36h3wuY35km3w'
# data = {
#     'grant_type': 'password'
#     , 'username': username
#     , 'password': password
# }
#
# user_agent = 'ham/0.1 by SPQRMP'
# headers = {
#     'User-Agent': user_agent
#     #, 'content-type': 'application/x-www-form-urlencoded'
# }
# #ret = requests.post('https://www.reddit.com/api/v1/access_token', params=data, auth=HTTPBasicAuth(client_id, secret)
#  #                   , headers=headers)
#
# #print(ret.json())
#
# new_headers = {
#     'User-Agent': user_agent
#     , 'Authorization': f'Bearer {access_token}'
# }
#
#
# latest_ret = requests.get('https://oauth.reddit.com/r/funny/hot', headers=new_headers)
#
# print(latest_ret)


if __name__ == '__main__':
    cnt = Controller.Controller('testing.db')
    cnt.build_symbol_list()
    cnt.populate_historical_data()

