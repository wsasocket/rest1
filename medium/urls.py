from django.conf.urls import url

from .views import (PersonalTasksCreateView, PersonalTasksListView,
                    ProjectCreateView, ProjectView, ReportCreateView,
                    ReportListView, UserGroupView, UserLoginView,
                    UserPasswordSetView, UserProfileView, UserRegistrationView)

urlpatterns = [
    # 用户注册
    url(r'^signup/', UserRegistrationView.as_view()),
    # 用户登录
    url(r'^signin/', UserLoginView.as_view()),
    # 更新用户密码，如果是个人有效token情况下，修改密码是修改自己的，否则只能让管理组成员修改指定用户密码
    url(r'^setpassword/(?P<id>[\w\-]{36})?/?$', UserPasswordSetView.as_view()),
    # 查询组信息，如果没有id就是查询全部组信息
    url(r'^group/(?P<gid>[\w\-]{36})?/?$', UserGroupView.as_view()),
    # 获取全部或者指定id的用户信息，没有参数就是自己的信息,all-对于管理组就是全部，对用group-leader就是全组
    url(r'^profile/(?P<option>all|[\w\-]{36})?/?$', UserProfileView.as_view()),

    # 创建项目，需要管理组权限
    url(r'^project/create/$', ProjectCreateView.as_view()),
    # 查看项目信息，可以指定项目id，需要用户权限
    url(r'^project/(?P<id>[\w\-]{36})?/?$', ProjectView.as_view()),

    # 个人创建自己的任务(task)，任务与project有关联
    url(r'^tasks/create/$', PersonalTasksCreateView.as_view()),

    # 查看自己(或者指定用户)的任务列表，默认只返回自己可继续执行的任务，包括正在启动和暂停的任务
    # all 代表获取自己全部的任务，st代表开始时间，et代表结束时间，et缺省的查询的当前时间，st缺省是本年度的1月1日
    # 虽然三个参数都为可选，但是et必须和st成对出现，没有st，et就会被识别为st！！！
    # 如果没有任何参数，就是查看自己且本年度正在进行或者暂停的项目
    # 如果指定ID就是查看指定用户的，但是需要一定的权限
    url(r'^tasks/(?P<uid>[\w\-]{36})?/?(?P<option>all|activate)?/?(?P<st>\d{4}-\d{2}-\d{2})?/?(?P<et>\d{4}-\d{2}-\d{2})?/?$',
        PersonalTasksListView.as_view()),

    # 创建自己的report
    url(r'^report/create/$', ReportCreateView.as_view()),
    # 根据和taskid获取相关report的信息，以更新时间排序
    # 如果task不是自己的，需要检查请求用户的权限。
    url(r'^report/(?P<task_id>[\w\- ]{36})/$',
        ReportListView.as_view()),
]
