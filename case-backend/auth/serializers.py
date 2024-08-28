from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from auth.models import User

class CustomSuperUserSerializer(serializers.ModelSerializer):
    #time_since_pub = serializers.SerializerMethodField()
    #username=serializers.StringRelatedField() #many to one tablosundan gelen bir kategori varsa ve o tabloda def __str__(self) varsa o kisimdaki ismi alir
    #username=CustomUserSerializer() #many to one tablosundan gelen bir kategori varsa vo tablodaki eşleşen değerleri alir
    class Meta:
        model= User
        fields=['username','email','password','first_name','last_name','is_active','adress']
        #exclude = ['username'] seklinde username'i kaldirabiliriz
        
    def validate_password(self, obj):
        validate_password(obj)
        return obj
    
class CustomUserAuthenticateSerializer(serializers.Serializer):
    username=serializers.CharField(required=True)
    password=serializers.CharField(required=True)
    
class CustomUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields=['first_name','last_name','adress'] #tümünü göstermek yerine ['username','email','password','first_name','last_name','active','adress'] yapabiliriz
        
    def validate(self, attrs):
        return super().validate(attrs)

class CustomUserRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model= User
        fields=['username','email','first_name','last_name','is_active','adress'] #tümünü göstermek yerine ['username','email','password','first_name','last_name','active','adress'] yapabiliriz
