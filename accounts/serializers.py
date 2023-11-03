# serializers.py
from rest_framework import serializers
from .models import *
import requests

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['image']

class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'username']

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'phone_number')
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password(user.password)
        user.save()
        data = {
        'expiry': 5,
        'length': 6,
        'medium': 'sms',
        'message': 'This is OTP from Vendyi, %otp_code%',
        'number': user.phone_number,
        'sender_id': 'Vendyi',
        'type': 'numeric',
        }

        headers = {
        'api-key': 'ZHNRdG1MbGVNallQV0FnZVBSTWg'
        }

        url = 'https://sms.arkesel.com/api/otp/generate'

        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            print(response.json())
        else:
            print(f"Error: {response.status_code} and {response.json()}")
        
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class FullUserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(source='userprofile')
    
    class Meta:
        model = User
        fields = ['id','first_name', 'last_name', 'email', 'phone_number', 'profile']

class UserOtpVerificationSerializer(serializers.Serializer):
    code = serializers.CharField()
    phone = serializers.CharField()