import requests
import os
import base64
import datetime
from urllib.parse import urlencode

url = "https://accounts.spotify.com/api/token"

class SpotifyApi(object):
    access_token = None
    access_token_expires = datetime.datetime.now()
    client_id = None
    client_secret = None

    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.client_id = client_id
        self.client_secret = client_secret

    def get_token_header(self):
        client_id = self.client_id
        client_secret = self.client_secret
        if client_id == None or client_secret==None:
            raise Exception("You must set client id and client secret!")
        client_creds = f"{self.client_id}:{self.client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())
        token_header = {
            "Authorization":f"Basic {client_creds_b64.decode()}"
        }
        return token_header

    def get_token_data(self):
        token_data = {
            "grant_type": "client_credentials"
        }
        return token_data

    def perform_auth(self):
        now = datetime.datetime.now()
        token_data = self.get_token_data()
        token_header = self.get_token_header()
        print(token_data,token_header)
        r = requests.post(url,data=token_data,headers=token_header)
        token_response_data = r.json()
        print(token_response_data)
        valid_request = r.status_code not in range(200,299)

        if valid_request:
            raise Exception("Could not Authenticate")

        access = token_response_data['access_token']
        self.access_token = access
        expires_in = token_response_data['expires_in']
        expires_in = now+ datetime.timedelta(seconds=expires_in)
        self.access_token_expires = expires_in
        did_expire = expires_in<now
        print(did_expire)
        return True

    def get_access_token(self):
        auth_done = self.perform_auth()
        if not auth_done:
            raise Exception("Authentication failed :(")
        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()
        if now > expires:
            self.perform_auth()
            return self.get_access_token()
        return token

    def get_resource_header(self,):
        access_token = self.access_token
        header = {
            "Authorization":f"Bearer {access_token}"
        }
        return header

    def search(self,query,search_type):
        header = self.get_resource_header()
        endpoint = "https://api.spotify.com/v1/search"
        data = urlencode({"q":query,"type":search_type.lower()})
        lookup_url = f"{endpoint}?{data}"
        print(lookup_url)
        r = requests.get(lookup_url,headers=header)
#         print(r.json())
        if r.status_code not in range(200,300):
            return {}
        return r.json()



    def get_resource(self,_id,resource_type="albums",version="v1"):
        endpoint = f"https://api.spotify.com/{version}/{resource_type}/{_id}"
        headers = self.get_resource_header()
        r = requests.get(endpoint,headers=headers)
        print(r.json())
        if r.status_code not in range(200,300):
            return {}
        return r.json()

    def get_album(self,_id):
        return self.get_resource(_id,"albums","v1")

    def get_artist(self,_id):
        return self.get_resource(_id,"artists","v1")
