from django.urls import path
from .views import *

urlpatterns = [
    path('fish/',insert_fish_details.as_view(), name='insert_fish_details'),
    ]