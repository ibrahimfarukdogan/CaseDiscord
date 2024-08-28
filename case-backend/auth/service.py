from datetime import datetime
from datetime import timezone
from django.utils.crypto import get_random_string
from .models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.core.mail import send_mail
from django.conf import settings
from django.core.files import File
from django.contrib.auth.hashers import make_password
from pathlib import Path
from io import BytesIO
import os


class UserOperations:  
    def login_authentication(self, username, password):
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                token, created = Token.objects.get_or_create(user=user)
                return {'message': token.key, 'status':True}
            else:
                return {'message': "user does not exist",'status':False}
        else:
            return {'message': "user is none",'status':False}
    def logout(self, request):
        try:
            Token.objects.get(user=request.user).delete()
        except(AttributeError):
            pass
        return {'message': "Logout successful"}
    def create_user(self, data):
        user = User.objects.create(
            username = data["username"],
            password= data["password"], 
            first_name= data["first_name"],
            last_name= data["last_name"],
            email= data["email"],
            adress= data["adress"],
        )
        user.set_password(data["password"])
        user.save()
        return user

    def get_token(self, user):
        token, created=Token.objects.get_or_create(user=user)
        return token.key
