from django.urls import path,include
from .views import *

urlpatterns = [
    path('get-user-token/', get_user_token, name="get_token"),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('verify/', UserOtpVerification.as_view(), name='verify'),
    path('update/user/', UserUpdateView.as_view(), name='user-update'),
    path('user/', UserListView.as_view(), name='user-list'),
    path('profile/', UserProfileUpdateView.as_view(), name='profile-update'),
    path('resend-otp/', UserResendOTP.as_view(), name='resend-otp'),
    path('verify-pin/', VerifyUserPinView.as_view(), name='verify-pin'),
    path('change-pin/', UserChangePinView.as_view(), name='change-pin'),
    path('check-phone/', CheckUserPhoneView.as_view(), name='check-phone'),
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('socialaccounts/', include('allauth.socialaccount.urls')),
    path('google/', GoogleLogin.as_view(), name='google_login'),

]
