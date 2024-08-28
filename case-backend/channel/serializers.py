from rest_framework import serializers
from channel.models import DiscordChannel

class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model= DiscordChannel
        fields=['name','description','token','token_type','token_secret','created_at','status']
        read_only_fields = ['created_at','status']

class ChannelUrlSerializer(serializers.Serializer):
    url = serializers.CharField(max_length=255)

class PostAuthVerifierSerializer(serializers.Serializer):
    org_id = serializers.IntegerField()
    oauth_token = serializers.CharField(max_length=255)
    oauth_verifier = serializers.CharField(max_length=255)
    
class ChannelAddSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)
    
class RemoveGroupChannelSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    
class RetrieveGroupChannelGuildSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    id = serializers.CharField(required=True)
 
class MessageGroupChannelSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    guild_id = serializers.CharField(required=True)
    channel_id = serializers.CharField(required=True)
    message = serializers.CharField(required=True)