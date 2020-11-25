"""
Created on Thu Dec  6 14:04:16 2019
@author: sambhav
"""
from django.conf.urls import url

from .views import (JobCreateView, JobListView, JobReportCreateView,
                    JobReportListView, ProjectView, ProjectViewCreate,
                    UserGroupView, UserGroupViewCreate, UserGroupViewUpdate,
                    UserLoginView, UserProfileView, UserRegistrationView)

urlpatterns = [
    # 用户注册
    url(r'^signup', UserRegistrationView.as_view()),
    # 用户登录
    url(r'^signin', UserLoginView.as_view()),
    # 查询组信息，如果没有id就是查询全部组信息
    url(r'^group/(?P<id>[\w\-]{36})?/?$', UserGroupView.as_view()),
    # 获取全部或者指定id的用户信息，没有参数就是自己的信息
    url(r'^profile/(?P<option>all|[\w\-]{36})?/?$', UserProfileView.as_view()),
    # 创建项目，需要管理组权限
    url(r'^project/create/$', ProjectViewCreate.as_view()),
    # 查看项目信息，可以指定项目id，需要用户权限
    url(r'^project/(?P<id>[\w\-]{36})?/?$', ProjectView.as_view()),

    #url(r'^jobs/$', JobListView.as_view()),
    #url(r'^jobs/create/$', JobCreateView.as_view()),
    #url(r'^jobs/report/(?P<job_id>[\w\-]{36})/$', JobReportListView.as_view()),
    #url(r'^jobs/report/create/$', JobReportCreateView.as_view()),
]
