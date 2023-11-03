from django.urls import path,include
from .views import *
from django.contrib.auth.views import PasswordResetConfirmView, PasswordResetCompleteView
urlpatterns = [
    path('get-user-token/', get_user_token, name="get_token"),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('verify/', UserOtpVerification.as_view(), name='verify'),
    path('update/user/<int:pk>/', UserUpdateView.as_view(), name='user-update'),
    path('user/<int:pk>/', UserListView.as_view(), name='user-list'),
    path('profile/<int:pk>/', UserProfileUpdateView.as_view(), name='profile-update'),
    path('', include('dj_rest_auth.urls')),
    path('password/reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password/reset/complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),


]
