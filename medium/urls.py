from django.conf.urls import url

from .views import (PersonalTasksCreateView, PersonalTasksListView,
                    ProjectCreateView, ProjectView, ReportCreateView,
                    ReportListView, UserGroupCreateView, UserGroupUpdateView,
                    UserGroupView, UserLoginView, UserProfileView,
                    UserRegistrationView)

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
    url(r'^project/create/$', ProjectCreateView.as_view()),
    # 查看项目信息，可以指定项目id，需要用户权限
    url(r'^project/(?P<id>[\w\-]{36})?/?$', ProjectView.as_view()),
    # 查看自己的任务列表，默认只返回自己可继续执行的任务，包括正在启动和暂停的任务
    # all 代表获取自己全部的任务，st代表开始时间，et代表结束时间，et缺省的查询的当前时间，st缺省是本年度的1月1日
    url(r'^tasks/(?P<option>all|activate)?/?(?P<st>\d{4}-\d{2}-\d{2})?/?(?P<et>\d{4}-\d{2}-\d{2})?/?$',
        PersonalTasksListView.as_view()),
    # 个人创建自己的任务(task)，任务与project有关联
    url(r'^tasks/create/$', PersonalTasksCreateView.as_view()),

    # 创建自己的report
    url(r'^tasks/report/create/$', ReportCreateView.as_view()),
    # 根据 人员的id和taskid获取相关report的信息，以更新时间排序
    # 如果user_id不是自己的，需要检查请求用户的权限。
    url(r'^tasks/report/(?P<tasks_id>[\w\-]{36})/(?P<userprofile_id>[\w\-]{36})?/?$',
        ReportListView.as_view()),
]
