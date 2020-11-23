"""
Created on Thu Dec  6 14:04:16 2019
@author: sambhav
"""
from django.conf.urls import url

from .views import (UserGroupView, UserGroupViewCreate, UserGroupViewUpdate,
                    UserLoginView, UserProfileView, UserRegistrationView,
                    ProjectViewCreate, ProjectView, JobListView, JobCreateView)

urlpatterns = [
    url(r'^signup', UserRegistrationView.as_view()),
    url(r'^signin', UserLoginView.as_view()),
    url(r'^profile', UserProfileView.as_view()),
    url(r'^group/(?P<id>[\w]{10,})?/?$', UserGroupView.as_view()),
    url(r'^group/create/$', UserGroupViewCreate.as_view()),
    url(r'^group/update/(?P<id>\w+)/$', UserGroupViewUpdate.as_view()),
    url(r'^project/(?P<id>[\w]{10,})?/?$', ProjectView.as_view()),
    url(r'^project/create/$', ProjectViewCreate.as_view()),
    url(r'^jobs/$', JobListView.as_view()),
    url(r'^jobs/create/$', JobCreateView.as_view()),

]
