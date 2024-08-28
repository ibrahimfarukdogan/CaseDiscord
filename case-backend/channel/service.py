from pathlib import Path
from io import BytesIO
from django.core.exceptions import SuspiciousOperation
from rest_framework import status
import requests
from django.conf import settings
import os

class ChannelOperations:
    def discord_auth_key(self, code):
        API_ENDPOINT = 'https://discord.com/api/v10/oauth2/token'
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': settings.CH_REDIRECT_GROUP,
            #'scope':'identify'
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        res = requests.post(API_ENDPOINT, data=data, headers=headers, auth=(settings.DISCORD_CLIENT_ID, settings.DISCORD_SECRET_KEY))
        res.raise_for_status()
        return res.json()
    
    def discord_auth_key_user(self, code):
        API_ENDPOINT = 'https://discord.com/api/v10'
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': settings.CH_REDIRECT_USER,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        res = requests.post('%s/oauth2/token' % API_ENDPOINT, data=data, headers=headers, auth=(settings.DISCORD_CLIENT_ID, settings.DISCORD_SECRET_KEY))
        res.raise_for_status()
        return res.json()
    
    def discord_refresh_token(refresh_token):
        API_ENDPOINT = 'https://discord.com/api/v10'
        data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
        }
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
        }
        res = requests.post(API_ENDPOINT+'/oauth2/token', data=data, headers=headers, auth=(settings.DISCORD_CLIENT_ID, settings.DISCORD_SECRET_KEY))
        res.raise_for_status()
        return res.json()
    
    def discord_get_user(self, access_token):
        API_ENDPOINT = 'https://discord.com/api/v10/users/@me'
        getdiscordresponse=requests.get(API_ENDPOINT,headers={"Authorization":'Bearer %s' % access_token})
        getdiscorduser=getdiscordresponse.json()
        return getdiscorduser

    def discord_get_guilds(self, access_token):
        API_ENDPOINT = 'https://discord.com/api/v10/users/@me/guilds'
        getdiscordresponse=requests.get(API_ENDPOINT,headers={"Authorization":'Bearer %s' % access_token})
        getdiscordguilds=getdiscordresponse.json()
        return getdiscordguilds
    
    def discord_retrieve_guild(self, guild_id):
        API_ENDPOINT = f'https://discord.com/api/v10/guilds/{guild_id}'
        getdiscordresponse=requests.get(API_ENDPOINT,headers={"Authorization":'Bot %s' % settings.DISCORD_BOT_KEY})
        getdiscordresponse.raise_for_status()
        getdiscordguilds=getdiscordresponse.json()
        return getdiscordguilds
    
    def discord_guild_messages(self, access_token, channel_id, message):
        API_ENDPOINT = f'https://discord.com/api/v10/channels/{channel_id}/messages' #https://discordapp.com/channels/1277903822064324698/1277905147200012288
        data = {
            "content":message
            #'scope':'identify'
        }
        headers = {
            "Authorization":'Bearer %s' % access_token,
            "Content-Type": "application/x-www-form-urlencoded"}
        
        res = requests.post(API_ENDPOINT, data=data, headers=headers)
        res.raise_for_status()
        return res.json()
    """def discord_guild_messages(self, guild_id, channel_id, message):
        API_ENDPOINT = f'https://discord.com/api/v10/channels/{channel_id}/messages' #https://discordapp.com/channels/1277903822064324698/1277905147200012288
        data = {
            "content":message
            #'scope':'identify'
        }
        headers = {
            "Authorization":'Bot %s' % settings.DISCORD_BOT_KEY,
            "Content-Type": "application/x-www-form-urlencoded"}
        
        res = requests.post(API_ENDPOINT, data=data, headers=headers)
        res.raise_for_status()
        return res.json()"""
    
    """
        API_ENDPOINT = 'https://discord.com/api/v10/users/@me/guilds/messages'
        data = {
            "content":"hello world",
            "tts":False,
            'grant_type': 'authorization_code',
            "Authorization":'Bearer %s' % access_token,
            'redirect_uri': settings.CH_REDIRECT_GROUP,
            #'scope':'identify'
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        res = requests.post(API_ENDPOINT, data=data, headers=headers, auth=(settings.DISCORD_CLIENT_ID, settings.DISCORD_SECRET_KEY))
        res.raise_for_status()
        return res.json()
    """