from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework import mixins,status

from .serializers import GroupSerializer, GroupMemberSerializer, RoleMemberGroupSerializer,RemoveGroupMemberSerializer
from .service import GroupOperations

from channel.serializers import ChannelUrlSerializer, ChannelSerializer,RemoveGroupChannelSerializer, RetrieveGroupChannelGuildSerializer,MessageGroupChannelSerializer
from channel.service import ChannelOperations
from channel.models import DiscordChannel

from group.models import WorkGroup, GroupMembers
from auth.models import User

from django.db import transaction
from django.conf import settings

class GroupApiView(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = GroupSerializer
    queryset = WorkGroup.objects.all()
    service = GroupOperations()
    
    def get_queryset(self):
        if self.action == "list" or self.action == "add_member" or self.action == "remove_member" or self.action == "get_all_members_from_group" or self.action == "change_member_role":
            return GroupMembers.objects.all()
        return WorkGroup.objects.all()
    
    def get_serializer_class(self):
        if self.action == "get_all_members_from_group" or self.action == "add_member" or self.action == "remove_member" or self.action == "change_member_role": #eger put gelirse serializer'ı değiştir
            return GroupMemberSerializer
        return GroupSerializer
    
    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            groupquery= WorkGroup.objects.filter(group_name=serializer.validated_data["group_name"]).first()
            #save etmeden once add member request.user yap
            member= GroupMembers.objects.create(member=request.user,
                                        added_to_group=groupquery, 
                                        role="admin")
            member.save()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def list(self, request, *args, **kwargs):
        #queryset = self.filter_queryset(self.get_queryset())
        #queryseti once groupmembers'a gore filtrele. Boylece uyenin bagli oldugu group id'leri aliriz
        #ardindan sonuctaki id'lere gore group'u filtrele ve listeyi dondur
        memberquery= GroupMembers.objects.filter(member=request.user).values_list('added_to_group_id')
        groupquery= WorkGroup.objects.filter(pk__in=memberquery)
        page = self.paginate_queryset(groupquery)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(groupquery, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        member= GroupMembers.objects.filter(member=request.user, added_to_group=kwargs["pk"]).first()
        if member is None or not member.role == "admin":
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    #group member urls
    @action(methods=["GET"], detail=True, url_path='get_members') #neden calismiyor
    def get_all_members_from_group(self, request, *args ,**kwargs):
        #filter all if user exists
        requestmembers=GroupMembers.objects.filter(added_to_group=kwargs["pk"])
        requestuser= GroupMembers.objects.filter(member=request.user, added_to_group=kwargs["pk"]).first()
        if not requestuser.role=="admin":
            return Response(status=status.HTTP_403_FORBIDDEN)
        if requestuser is None or requestmembers is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        page = self.paginate_queryset(requestmembers)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(requestmembers, many=True)
        return Response(serializer.data)
    
    @action(methods=["POST"], detail=True, url_path=r'add_member')
    def add_member(self, request, *args ,**kwargs):
        serializer = RoleMemberGroupSerializer(data=request.data, context={"request":request}) #kwargs'ıda gondermeli ?
        serializer.is_valid(raise_exception=True)
        
        group=WorkGroup.objects.get(pk=kwargs["pk"]) #?
        adduser=User.objects.get(email=serializer.validated_data.get('email', None))
        requestuser= GroupMembers.objects.filter(member=request.user, added_to_group=kwargs["pk"]).first()
        if not requestuser.role=="admin":
            return Response(status=status.HTTP_403_FORBIDDEN)
        if group is None or adduser is None or requestuser is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if GroupMembers.objects.filter(added_to_group=group, member=adduser).first():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        member= GroupMembers.objects.create(member=adduser,
                                    added_to_group=group, 
                                    role=serializer.validated_data.get('role', None))
        member.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
   
    @action(methods=["POST"], detail=True, url_path=r'remove_member')
    def remove_member(self, request, *args ,**kwargs):
        serializer = RemoveGroupMemberSerializer(data=request.data, context={"request":request}) #user'ı göndermek için yaptık
        serializer.is_valid(raise_exception=True)
        
        group=WorkGroup.objects.get(pk=kwargs["pk"]) #?
        removeuser=User.objects.filter(email=serializer.validated_data.get('email', None)).first()
        requestuser= GroupMembers.objects.filter(member=request.user, added_to_group=kwargs["pk"]).first()
        removemember=GroupMembers.objects.filter(member=removeuser).first()
        if not requestuser.role=="admin":
            return Response(status=status.HTTP_403_FORBIDDEN)
        if group is None or removeuser is None or requestuser is None or removemember is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        removemember.delete()
        return Response(status=status.HTTP_200_OK)
    
    @action(methods=["PATCH"], detail=True, url_path=r'change_member_role')
    def change_member_role(self, request, *args ,**kwargs):
        serializer = RoleMemberGroupSerializer(data=request.data, context={"request":request}) #user'ı göndermek için yaptık
        serializer.is_valid(raise_exception=True)
        
        group=WorkGroup.objects.get(pk=kwargs["pk"]) #?
        changeuser=User.objects.filter(email=serializer.validated_data.get('email', None)).first()
        requestuser= GroupMembers.objects.filter(member=request.user, added_to_group=kwargs["pk"]).first()
        if not requestuser.role=="admin":
            return Response(status=status.HTTP_403_FORBIDDEN)
        if group is None or changeuser is None or requestuser is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        changeuser.role=serializer.validated_data.get('role', None)
        changeuser.save()
        return Response(status=status.HTTP_200_OK)

    @action(methods=["GET"], detail=True, url_path=r'get_url')
    def get_ch_url_for_org(self, request, *args, **kwargs):
        
        serializer= ChannelUrlSerializer
        group=WorkGroup.objects.get(pk=kwargs["pk"])
        requestuser= GroupMembers.objects.filter(member=request.user, added_to_group=kwargs["pk"]).first()
        if not requestuser.role=="admin":
            return Response(status=status.HTTP_403_FORBIDDEN)
        if group is None or requestuser is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        url=(f"https://discord.com/oauth2/authorize?client_id={settings.DISCORD_CLIENT_ID}&"
             f"response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fapi%2Fworkgroup%2Fredirect%2F&"
             f"scope=identify+guilds&state={group.id}") #+messages.write ?
        #serializer.is_valid(raise_exception=True)
        #return redirect(serializer.validated_data.get('url', None))
        return Response({"url": url}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["GET"], url_path="redirect", url_name="redirect")
    def redirect(self, request, *args, **kwargs):
        code=request.GET.get("code")
        state=request.GET.get("state")
        service = ChannelOperations()
        group=WorkGroup.objects.get(pk=state)
        requestuser= GroupMembers.objects.filter(member=request.user, added_to_group_id=state).first()
        if not requestuser.role=="admin":
            return Response(status=status.HTTP_403_FORBIDDEN)
        credentials=service.discord_auth_key(code)
        
        if credentials == None or group is None or requestuser is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        access_token=credentials['access_token']
        token_type=credentials['token_type'].lower()
        refresh_token=credentials['refresh_token']
        
        discordresponse = service.discord_get_user(access_token)  # get account info (name, id, logo)
        print("discorduser: ",discordresponse)
        name=discordresponse['username']
        acc_id=discordresponse['id']
        channel = DiscordChannel.objects.filter(discord_id=acc_id, added_by_group=group).first()
        if discordresponse == None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if channel:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if not channel:
            channel = DiscordChannel()
            channel.discord_id = acc_id
            channel.status = True
            channel.added_by_group = group
        channel.name = name
        channel.description = f"this -{name}- channel added by {request.user.username} to {group.group_name} WorkGroup"
        channel.token = access_token
        channel.token_type = token_type
        channel.token_secret = refresh_token
        if channel.status == False:
            channel.status = True
        channel.save()
        return Response(status=status.HTTP_200_OK)
        
    @action(methods=["GET"], detail=True, url_path="channel_list")
    def list_ch(self, request, *args, **kwargs):
        #filter all if user exists
        requestchannels=DiscordChannel.objects.filter(added_by_group=kwargs["pk"])
        requestuser= GroupMembers.objects.filter(member=request.user, added_to_group=kwargs["pk"]).first()
        if not requestuser.role=="admin":
            return Response(status=status.HTTP_403_FORBIDDEN)
        if requestuser is None or requestchannels is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        page = self.paginate_queryset(requestchannels)
        if page is not None:
            serializer = ChannelSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ChannelSerializer(requestchannels, many=True)
        return Response(serializer.data)

    @action(methods=["POST"], detail=True, url_path="channel_remove")
    def remove_ch(self, request, *args, **kwargs):
        serializer = RemoveGroupChannelSerializer(data=request.data, context={"request":request}) #user'ı göndermek için yaptık
        serializer.is_valid(raise_exception=True)
        
        group=WorkGroup.objects.get(pk=kwargs["pk"]) #?
        requestuser= GroupMembers.objects.filter(member=request.user, added_to_group=kwargs["pk"]).first()
        channel = DiscordChannel.objects.filter(name=serializer.validated_data.get('name', None), added_by_group=group).first()
        if not requestuser.role=="admin":
            return Response(status=status.HTTP_403_FORBIDDEN)
        if group is None or channel is None or requestuser is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        channel.delete()
        return Response(status=status.HTTP_200_OK)
    
    @action(methods=["GET"], detail=True, url_path="channel_guilds_list")
    def ch_guilds(self, request, *args, **kwargs):
        serializer = RemoveGroupChannelSerializer(data=request.data, context={"request":request}) #user'ı göndermek için yaptık
        serializer.is_valid(raise_exception=True)
        
        service = ChannelOperations()
        requestchannels=DiscordChannel.objects.filter(name=serializer.validated_data.get('name', None), added_by_group=kwargs["pk"]).first()
        requestuser= GroupMembers.objects.filter(member=request.user, added_to_group=kwargs["pk"]).first()
        if requestuser is None or requestchannels is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        credentials=service.discord_get_guilds(requestchannels.token)
        return Response({"guilds": credentials}, status=status.HTTP_200_OK)

    @action(methods=["GET"], detail=False, url_path="channel_guild_retrieve")
    def ch_guild_retrieve(self, request, *args, **kwargs):
        serializer = RetrieveGroupChannelGuildSerializer(data=request.data, context={"request":request}) #user'ı göndermek için yaptık
        serializer.is_valid(raise_exception=True)
        service = ChannelOperations()
        requestchannels=DiscordChannel.objects.filter(name=serializer.validated_data.get('name', None), added_by_group=kwargs["pk"]).first()
        print("channel: ",requestchannels," token: ",requestchannels.token)
        if requestchannels is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        credentials=service.discord_retrieve_guild(serializer.validated_data.get('id', None))
        return Response({"guild": credentials}, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=True, url_path="channel_guild_message")
    def ch_guild_message(self, request, *args, **kwargs):
        serializer = MessageGroupChannelSerializer(data=request.data, context={"request":request}) #user'ı göndermek için yaptık
        serializer.is_valid(raise_exception=True)
        
        service = ChannelOperations()
        requestchannels=DiscordChannel.objects.filter(name=serializer.validated_data.get('name', None), added_by_group=kwargs["pk"]).first()
        requestuser= GroupMembers.objects.filter(member=request.user, added_to_group=kwargs["pk"]).first()
        if requestuser is None or requestchannels is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        credentials=service.discord_guild_messages(requestchannels.token,
                                                   serializer.validated_data.get('channel_id', None),
                                                   serializer.validated_data.get('message', None))
        return Response({"guilds": credentials}, status=status.HTTP_200_OK)

        
        
       