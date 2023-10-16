from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializers import *
from .models import User
from rest_framework import generics, status
from django.contrib.auth import authenticate, login, logout
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
# Create your views here.
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
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            user = User.objects.get(username=request.data['username'])
            token, _ = Token.objects.get_or_create(user=user)
            response.data['token'] = token.key
        return response

class UserOtpVerification(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserOtpVerificationSerializer
    
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        code = serializer.validated_data.get('code')
        phone = serializer.validated_data.get('phone')
        data = {
            "code": code,
            "number": phone,
        }

        headers = {
        'api-key': 'ZHNRdG1MbGVNallQV0FnZVBSTWg'
        }

        url = 'https://sms.arkesel.com/api/otp/verify'

        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200 and response.json().get("message") == "Successful":
            print(response.json())
            user = User.objects.get(phone_number=phone)
            user.is_active = True
            user.save()
            return Response({"message": "User is verified"}, status=200)
        elif response.status_code == 200 and response.json().get("message") == "Code has expired":
            return Response({"message": "Code has expired"}, status=400)
        elif response.status_code == 200 and response.json().get("message") == "Invalid code":
            return Response({"message": "Invalid code"}, status=400)
        else:
            print(f"Error: {response.status_code} and {response.json()}")
            return Response({"message": "Code incorrect"}, status=400)
       
class UserLoginView(generics.CreateAPIView):
    serializer_class = UserLoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise AuthenticationFailed(detail="Invalid username")

        user = authenticate(username=username, password=password)
        if user is None:
            raise AuthenticationFailed(detail="Invalid password")

        token, _ = Token.objects.get_or_create(user=user)

        # Log the user in within the session
        login(request, user)

        return Response({"message": "Login successful", "token": token.key}, status=status.HTTP_200_OK)

class UserLogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        logout(request)
        return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)

class UserUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserProfileUpdateView(generics.UpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    
class UserListView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = FullUserSerializer