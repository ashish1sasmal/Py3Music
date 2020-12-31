from django.shortcuts import render,redirect

# Create your views here.

import requests
import os
import base64
import datetime
from urllib.parse import urlencode
from django.views.generic import View
from .spotify import SpotifyApi
from collections import defaultdict as dd

CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')


sp = SpotifyApi(CLIENT_ID, CLIENT_SECRET)
sp.perform_auth()

class Home(View):
    def get(self,request,*args,**kwargs):
        return render(request,"music/home.html")

    def post(self,request,*args,**kwargs):
        search_text = request.POST.get("gen_search")
        print(search_text)
        search_response = sp.search(search_text,"track")
        list_items = search_response['tracks']['items']
        items=[]
        for i in list_items:
            # print(i)
            f=dd()
            t_url = i['uri'].split(":")[2]
            f["url"]=t_url
            f["name"]=i['name']
            f["popularity"]=i["popularity"]
            items.append(f)

        items.sort(reverse=True,key = lambda x:x['popularity'])

        context = {"items":items}
        print(len(items))
        return render(request,"music/search.html",context)
