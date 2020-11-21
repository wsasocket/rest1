"""
Created on Thu Dec  6 14:04:16 2019
@author: sambhav
"""
from django.conf.urls import url

from .views import UserRegistrationView, UserLoginView, UserProfileView

urlpatterns = [
    url(r'^signup', UserRegistrationView.as_view()),
    url(r'^signin', UserLoginView.as_view()),
    url(r'^profile', UserProfileView.as_view()),
]
