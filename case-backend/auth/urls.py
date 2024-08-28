from django.urls import path,include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'guests', views.GuestUserApiView, basename='guest')
router.register(r'users', views.CustomUserApiView, basename='user')
router.register(r'superusers', views.SuperUserApiView, basename='superuser')#auth??

urlpatterns = [
    path(r'', include(router.urls)),
]
