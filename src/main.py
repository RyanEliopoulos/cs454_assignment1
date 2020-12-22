import requests
import json


"""

    NOTES:
        Redirect URL is set to http://localhost:8080

        So when I attempt to authenticate, does that mean I need to listen on that port to get the tokens or
        will those be supplied in the requests response?

"""

with open('../resources/config.json', 'r') as config_file:
    json_rep = json.load(config_file)
    username = json_rep['username']
    password = json_rep['password']
    client_id = json_rep['client_id']
    secret = json_rep['secret']


data = {
    'grant_type': 'password'
    , 'username': username
    , 'pas sword': password
}

headers = {
    'User-agent': 'SPQR'
    , 'con tent-type': 'application/x-www-form-urlencoded'
}
ret = requests.post('https://www.reddit.com/api/v1/access_token', params=data, auth=(client_id, secret)
                    , headers=headers)

print(ret.content)
print('hello')
