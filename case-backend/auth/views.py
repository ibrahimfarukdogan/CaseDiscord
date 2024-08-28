from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework import mixins
from rest_framework import status

from .serializers import CustomSuperUserSerializer, CustomUserAuthenticateSerializer,CustomUserUpdateSerializer,CustomUserRetrieveSerializer
from .service import UserOperations

from auth.models import User

from channel.serializers import ChannelUrlSerializer,ChannelSerializer,RemoveGroupChannelSerializer
from channel.models import DiscordChannel
from channel.service import ChannelOperations

from django.conf import settings

class GuestUserApiView(mixins.CreateModelMixin, GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = CustomSuperUserSerializer
    queryset = User.objects.all()
    service = UserOperations()

    def create(self, request, *args, **kwargs):
        if request.auth:
            if Token.objects.filter(request.auth).exists():
                return Response(status=status.HTTP_307_TEMPORARY_REDIRECT)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.service.create_user(serializer.validated_data)  
        token = self.service.get_token(user)
        self.request.user.auth=token
        return Response(serializer.data, status=status.HTTP_201_CREATED) 
    
    @action(methods=["POST"], detail=False, url_path="login") #api/users/changepassword
    def login(self, request):
        serializer = CustomUserAuthenticateSerializer(data=request.data) #user'ı göndermek için yaptık
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        result=self.service.login_authentication(data['username'], data['password'])
        if result['status']:
            return Response(result['message'], status= status.HTTP_200_OK)
        return Response(result['message'], status= status.HTTP_404_NOT_FOUND)
    
class CustomUserApiView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomSuperUserSerializer
    queryset = User.objects.all()
    service = UserOperations()
    
    def get_serializer_class(self):
        if self.action == "retrieve": #eger get gelirse serializer'ı değiştir
            return CustomUserRetrieveSerializer
        if self.action == "update" or self.action == "perform_update" or self.action == "partial_update": #eger put gelirse serializer'ı değiştir
            return CustomUserUpdateSerializer
        return CustomSuperUserSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance != request.user: #her zaman kullanıcının kendisini dondurur
            instance =request.user
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)  

    @action(methods=["POST"], detail=False, url_path="logout")
    def logout(self, request):
        result=self.service.logout(request)
        return Response(result['message'])
    
    @action(methods=["GET"], detail=False, url_path=r'get_url')
    def get_ch_url_for_user(self, request, *args, **kwargs):
        
        serializer= ChannelUrlSerializer
        channel = DiscordChannel.objects.filter(added_by_user=request.user).first()
        if channel:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        url=(f"https://discord.com/oauth2/authorize?client_id={settings.DISCORD_CLIENT_ID}&"
             f"response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fapi%2Fusers%2Fredirect%2F&"
             f"scope=identify+guilds")
        #serializer.is_valid(raise_exception=True)
        #return redirect(serializer.validated_data.get('url', None))
        return Response({"url": url}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["GET"], url_path="redirect", url_name="redirect")
    def redirect(self, request, *args, **kwargs):
        code=request.GET.get("code")
        service = ChannelOperations()
        
        credentials=service.discord_auth_key_user(code)
        
        if credentials == None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        access_token=credentials['access_token']
        token_type=credentials['token_type'].lower()
        refresh_token=credentials['refresh_token']
        
        discordresponse = service.discord_get_user(access_token)  # get account info (name, id, logo)
        print("discorduser: ",discordresponse)
        name=discordresponse['username']
        acc_id=discordresponse['id']
        channel = DiscordChannel.objects.filter(discord_id=acc_id, added_by_user=request.user).first()
        if discordresponse == None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if channel:
            return Response(status=status.HTTP_403_FORBIDDEN)
        channel = DiscordChannel()
        channel.discord_id = acc_id
        channel.status = True
        channel.added_by_user = request.user
        channel.name = name
        channel.description = f"this -{name}- channel added by {request.user.username} named user"
        channel.token = access_token
        channel.token_type = token_type
        channel.token_secret = refresh_token
        if channel.status == False:
            channel.status = True
        channel.save()
        return Response(status=status.HTTP_200_OK)

    @action(methods=["GET"], detail=False, url_path="channel_list")
    def list_ch(self, request, *args, **kwargs):
        #filter all if user exists
        requestchannels=DiscordChannel.objects.filter(added_by_user=request.user)
        if requestchannels is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        page = self.paginate_queryset(requestchannels)
        if page is not None:
            serializer = ChannelSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ChannelSerializer(requestchannels, many=True)
        return Response(serializer.data)

    @action(methods=["POST"], detail=False, url_path="channel_remove")
    def remove_ch(self, request, *args, **kwargs):
        channel = DiscordChannel.objects.filter(added_by_user=request.user).first()
        if channel is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        channel.delete()
        return Response(status=status.HTTP_200_OK)
    
    @action(methods=["GET"], detail=False, url_path="channel_guilds_list")
    def ch_guilds(self, request, *args, **kwargs):
        service = ChannelOperations()
        channel = DiscordChannel.objects.filter(added_by_user=request.user).first()
        print("channel: ",channel)
        if channel is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        credentials=service.discord_get_guilds(channel.token)
        return Response({"guilds": credentials}, status=status.HTTP_200_OK)

    @action(methods=["GET"], detail=False, url_path="channel_guild_retrieve")
    def ch_guild_retrieve(self, request, *args, **kwargs):
        serializer = RemoveGroupChannelSerializer(data=request.data, context={"request":request}) #user'ı göndermek için yaptık
        serializer.is_valid(raise_exception=True)
        service = ChannelOperations()
        channel = DiscordChannel.objects.filter(added_by_user=request.user).first()
        print("channel: ",channel," token: ",channel.token)
        if channel is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        credentials=service.discord_retrieve_guild(serializer.validated_data.get('name', None))
        return Response({"guild": credentials}, status=status.HTTP_200_OK)
        
class SuperUserApiView(ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = CustomSuperUserSerializer
    queryset = User.objects.all()
