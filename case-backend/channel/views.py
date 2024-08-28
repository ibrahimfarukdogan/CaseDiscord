from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework import mixins
from rest_framework import status
from .serializers import GroupSerializer, GroupMemberSerializer, RoleMemberGroupSerializer,RemoveGroupMemberSerializer

from group.models import WorkGroup, GroupMembers
from auth.models import User

class ChannelApiView(ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = GroupSerializer
    queryset = WorkGroup.objects.all()
       
    # def retrieve(self, request, *args, **kwargs):
        # instance = self.get_object()
        # if instance != request.user: #her zaman kullanıcının kendisini dondurur
        #     instance =request.user
        #     serializer = self.get_serializer(instance)
        #     return Response(serializer.data)
        # serializer = self.get_serializer(instance)
        # return Response(serializer.data)