from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializers import *
from .models import User
import os
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authentication import TokenAuthentication,SessionAuthentication
from rest_framework import generics, status
from django.contrib.auth import authenticate, login, logout
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.views.decorators.csrf import csrf_exempt
CALLBACK_URL_YOU_SET_ON_GOOGLE = os.environ.get('CALLBACK_URL_YOU_SET_ON_GOOGLE')

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = CALLBACK_URL_YOU_SET_ON_GOOGLE
    client_class = OAuth2Client

@api_view(["GET"])
def get_user_token(request):
    user = request.user

    # Check if a token already exists for the user
    token, created = Token.objects.get_or_create(user=user)
    key = token.key
    user = token.user.username
    return Response({'key':key,"user":user})

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]  # Allow anyone to register

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            if response.status_code == status.HTTP_201_CREATED:
                user = User.objects.get(username=request.data['username'])
                token, _ = Token.objects.get_or_create(user=user)
                user_id = user.id
                response.data['token'] = token.key
                response.data['user_id'] = user_id
            return response
        except ExternalAPIError as e:
            # Here you can customize the response as per your frontend requirements
            return Response({"error": str(e)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
class UserOtpVerification(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserOtpVerificationSerializer
    
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        code = serializer.validated_data.get('code')
        user_id = serializer.validated_data.get('user_id')
        phone = User.objects.get(pk=user_id).phone_number
        data = {
            "code": code,
            "number": phone,
        }

        headers = {
        'api-key': os.environ.get('ARK_API_KEY'),
        }

        url = 'https://sms.arkesel.com/api/otp/verify'

        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200 and response.json().get("message") == "Successful":
            print(response.json())
            user = User.objects.get(pk=user_id)
            user.is_active = True
            user.save()
            return Response({"message": "User is verified"}, status=200)
        elif response.status_code == 200 and response.json().get("message") == "Code has expired":
            return Response({"message": "Code has expired"}, status=400)
        elif response.status_code == 200 and response.json().get("message") == "Invalid code":
            return Response({"message": "Code incorrect"}, status=400)
        else:
            print(f"Error: {response.status_code} and {response.json()}")
            return Response({"message": "Code incorrect"}, status=400)

@method_decorator(csrf_exempt, name='dispatch')      
class UserLoginView(generics.CreateAPIView):
    serializer_class = UserLoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email)
            if user.is_active == False:
                raise AuthenticationFailed(detail="User is not verified",status_code=400)
        except User.DoesNotExist:
            raise AuthenticationFailed(detail="Invalid email",status_code=400)
    
        user = authenticate(username=email, password=password)
        if user is None:
            raise AuthenticationFailed(detail="Invalid password",status_code=400)

        token, _ = Token.objects.get_or_create(user=user)

        csrf_token = get_token(request)
        if csrf_token is not None:
            # Log the user in within the session
            login(request, user)

        return Response({"message": "Login successful", "token": token.key}, status=status.HTTP_200_OK)

class UserLogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication,SessionAuthentication]
    def get(self, request, *args, **kwargs):
        logout(request)
        return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)

class UserUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UserProfileUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    serializer_class = UserProfileSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_object(self):
        return UserProfile.objects.get(user=self.request.user)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UserListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication,SessionAuthentication]
    serializer_class = FullUserSerializer
    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.id)

class UserResendOTP(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserResendOtpSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone = User.objects.get(pk=serializer.validated_data.get('user_id')).phone_number
        user_id = serializer.validated_data.get('user_id')
        user = User.objects.get(pk=user_id)
        message = f"Hello {user.username}, Welcome to Vendyi."
        data = {
        'expiry': 5,
        'length': 6,
        'medium': 'sms',
        'message': message+' This is your verification code:\n%otp_code%\nPlease do not share this code with anyone.',
        'number': phone,
        'sender_id': 'Vendyi',
        'type': 'numeric',
        }

        headers = {
        'api-key': os.environ.get('ARK_API_KEY'),
        }

        url = 'https://sms.arkesel.com/api/otp/generate'

        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200 and response.json().get("code") == 1000:
            print(response.json())
            return Response({"message": "OTP sent"}, status=200)
        else:
            print(f"Error: {response.status_code} and {response.json()}")
            return Response({"message": "OTP not sent"}, status=400)

class VerifyUserPinView(generics.CreateAPIView):
    serializer_class = VerifyUserPinSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        pin = serializer.validated_data['pin']
        
        if request.user.pin == pin:
            return Response({"message": "Pin is correct"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Pin is incorrect"}, status=status.HTTP_400_BAD_REQUEST)