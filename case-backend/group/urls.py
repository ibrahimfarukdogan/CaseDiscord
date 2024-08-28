from django.urls import path,include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'workgroup', views.GroupApiView, basename='workgroup')
#router.register(r'workgroupmembers', views.GroupMembersApiView, basename='workgroupmembers')
#router.register(r'channel', views.ChannelApiView, basename='channel')

urlpatterns = [
    path(r'', include(router.urls)),
]
