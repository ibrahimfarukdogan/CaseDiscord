import os
from django.db import models
from django.contrib.auth.models import AbstractUser

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

class User(AbstractUser): #abstracuser yani django'nun user tablosunu override eden tabloyu çalıştırmak için settingste auth_user_model ekleyip, adminde çağırırız
    adress=models.CharField(max_length=50, null=True)
    
@receiver(post_save, sender=settings.AUTH_USER_MODEL) #kayit olma sinyali gelidiginde token olusturur
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)