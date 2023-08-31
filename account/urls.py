from django.urls import path
from .views import *

urlpatterns = [
    path('get-user-token/', get_user_token, name="get_token")
]
