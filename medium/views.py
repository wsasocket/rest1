from django.shortcuts import render

# Create your views here.
"""
Created on Thu Dec  6 14:04:16 2019
@author: sambhav
"""
from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from rest_framework import status
from rest_framework.generics import (CreateAPIView, ListAPIView,
                                     RetrieveAPIView, UpdateAPIView)
from rest_framework.permissions import (AllowAny, BasePermission,
                                        IsAuthenticated)
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from .models import PersonalTasks, Projects, Reports, UserGroup, UserProfile
from .permissions import MustStuffGroupPermission, NeedLeaderPermission
from .serializers import (PersonalTasksSerializer, ProjectsSerializer,
                          ReportCreateSerializer, ReportSerializer,
                          UserGroupSerializer, UserLoginSerializer,
                          UserProfileSerializer, UserRegistrationSerializer,
                          UserSerializer, UserSetPasswordSerializer)


class UserRegistrationView(CreateAPIView):
    # 用户注册视图
    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny,)  # 允许所有访问

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)
        serializer.save()
        status_code = status.HTTP_201_CREATED
        response = {
            'success': 'true',
            'status code': status_code,
            'message': '用户成功注册',
        }
        return Response(response, status=status_code)


class UserLoginView(RetrieveAPIView):
    # 用户登录视图
    permission_classes = (AllowAny,)
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = {
            'success': 'true',
            'status code': status.HTTP_200_OK,
            'message': '用户成功登录',
            'name': serializer.data['username'],
            'email': serializer.data['email'],
            'token': serializer.data['token'],
        }
        status_code = status.HTTP_200_OK
        return Response(response, status=status_code)


class UserPasswordSetView(UpdateAPIView):
    permission_classes = (IsAuthenticated,)  # 必须验证授权的用户
    authentication_class = JSONWebTokenAuthentication  # 使用这个方法验证授权信息
    serializer_class = UserSetPasswordSerializer

    def put(self, request, **kwargs):
        user = request.user
        profile_id = kwargs.get('id', None)
        result = None
        s = None
        u = None
        target_user = None
        if profile_id:
            target_user = UserProfile.objects.filter(id=profile_id).first()
            if target_user is None:
                return Response({'detail': '指定用户不存在'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                target_user = target_user.user

        if user.profile.group.level == 100:
            # 管理员改用户密码
            if target_user:
                s = self.serializer_class(target_user, data=request.data)
                u = target_user
        elif user.profile.is_group_leader:
            # leader可以重置自己组成员的数据
            if target_user:
                if user.profile.group.id == target_user.profile.group.id:
                    s = self.serializer_class(target_user, data=request.data)
                    u = target_user
                else:
                    return Response({'detail': '你无权重置指定用户的Password'}, status=status.HTTP_403_FORBIDDEN)
        if not target_user:
            # 处理自己的passwd
            s = self.serializer_class(user, data=request.data)
            u = user
        s.is_valid()
        if isinstance(s.save(), User):
            result = {'result': '{}更新口令成功'.format(u.username)}
        else:
            result = {'result': '{}更新口令失败'.format(u.username)}
        return Response(result, status=status.HTTP_200_OK)


class UserProfileView(ListAPIView):

    permission_classes = (IsAuthenticated,)  # 必须验证授权的用户
    authentication_class = JSONWebTokenAuthentication  # 使用这个方法验证授权信息
    serializer_class = UserProfileSerializer

    def get(self, request, **kwargs):
        # 如果有option 参数先验证基本的权限，再根据参数性质进行检索
        option = kwargs.get('option', None)
        select_users = None
        if option == 'all':
            if request.user.profile.group.level != 100:
                if request.user.profile.is_group_leader:
                    select_users = UserProfile.objects.filter(
                        group=request.user.profile.group).all()
                else:
                    return Response({'detail': '你不是管理组成员也不是Group Leader，无权查看所属人员信息'}, status=status.HTTP_403_FORBIDDEN)
            else:
                select_users = UserProfile.objects.all()
            s = self.serializer_class(select_users, many=all)
            return Response(s.data, status=status.HTTP_200_OK)
        if option is not None:
            # UUID
            if not any((request.user.profile.is_group_leader, (request.user.profile.group.level == 100))):
                return Response({'detail': '你不是Group Leader，无权查看人员信息'}, status=status.HTTP_403_FORBIDDEN)
            select_user = UserProfile.objects.filter(id=option).first()
            if select_user is None:
                return Response({'detail': "用户id不正确"}, status=status.HTTP_200_OK)

            if request.user.profile.group.id != select_user.group.id:
                return Response({'detail': '你不是这个组的Group Leader，无权查看相关人员信息'}, status=status.HTTP_403_FORBIDDEN)
            s = self.serializer_class(select_user)
            return Response(s.data, status=status.HTTP_200_OK)

        # 查询自己的档案
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            status_code = status.HTTP_200_OK
            s = self.serializer_class(user_profile)
            return Response(s.data, status=status_code)

        except Exception as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response = {
                'success': 'false',
                'status code': status.HTTP_400_BAD_REQUEST,
                'message': 'User does not exists',
                'error': str(e)
            }
            return Response(response, status=status_code)


class UserGroupView(RetrieveAPIView):
    permission_classes = (AllowAny, )  # 必须验证授权的用户
    serializer_class = UserGroupSerializer

    def get(self, request, **kwarg):
        # 传统的 ?name=xxxx 的方法
        # name = request.query_params.get('name', None)
        s = None
        if 'gid' not in kwarg.keys():
            # 枚举所有的组信息
            groups = UserGroup.objects.order_by('-id').all()
            s = self.serializer_class(groups, many=True)
        else:
            # 枚举指定组信息
            groups = UserGroup.objects.filter(id=kwarg['gid']).first()
            # 直接将数据库的结果导入到serializer中就能得到完美的结果
            s = self.serializer_class(groups)
        return Response(s.data, status=status.HTTP_200_OK)


# class UserGroupCreateView(CreateAPIView):
#     permission_classes = (IsAuthenticated, )  # 必须验证授权的用户
#     authentication_class = JSONWebTokenAuthentication  # 使用这个方法验证授权信息
#     serializer_class = UserGroupSerializer
#     # 增加新的组

#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         response = {
#             'success': 'True',
#             'status code': status.HTTP_201_CREATED,
#             'message': 'Group Add successfully',
#             'name': serializer.data['name'],
#             'level': serializer.data['level'],
#         }
#         return Response(response, status=status.HTTP_201_CREATED)


# class UserGroupUpdateView(UpdateAPIView):

#     permission_classes = (IsAuthenticated, )  # 必须验证授权的用户
#     authentication_class = JSONWebTokenAuthentication  # 使用这个方法验证授权信息
#     serializer_class = UserGroupSerializer
#     # 在 url.py中设置正则名为 一致
#     # 就是说通过url设置查询的关键字 ，这个框架自动化的地方在于把 lookup_field queryset
#     # 设置好会自动过滤出需要的数据set，在serializer类中可以修改保存
#     # lookup_field = 'id'  # 注意在请求url中的正则表达式
#     # queryset = UserGroup.objects.all()
#     # 修改组的信息

#     def patch(self, request, **kwargs):
#         instance = UserGroup.objects.filter(id=kwargs['id']).first()
#         serializer = self.serializer_class(instance, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         response = {
#             'success': 'True',
#             'status code': status.HTTP_200_OK,
#             'message': 'Group Modify successfully',
#             'name': serializer.data['name'],
#             'level': serializer.data['level'],
#         }
#         return Response(response, status=status.HTTP_202_ACCEPTED)


class ProjectView(RetrieveAPIView):
    authentication_class = JSONWebTokenAuthentication
    permission_classes = (IsAuthenticated,)
    serializer_class = ProjectsSerializer
    # 枚举所有的组信息

    def get(self, request, **kwarg):
        # name = request.query_params.get('name', None)

        if 'id' not in kwarg.keys():
            projects = Projects.objects.all()
            s = self.serializer_class(projects, many=True)
        else:
            projects = Projects.objects.filter(id=kwarg['id']).first()
            s = self.serializer_class(projects)
        return Response(s.data, status=status.HTTP_200_OK)


class ProjectCreateView(CreateAPIView):
    serializer_class = ProjectsSerializer
    authentication_class = JSONWebTokenAuthentication
    permission_classes = (IsAuthenticated, MustStuffGroupPermission)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {
            'success': 'True',
            'status code': status.HTTP_201_CREATED,
            'message': 'Project Create Successfully',
            'more': serializer.data
        }
        return Response(response, status=status.HTTP_201_CREATED)


class PersonalTasksListView(ListAPIView):
    permission_classes = (IsAuthenticated, )  # 必须验证授权的用户
    authentication_class = JSONWebTokenAuthentication
    serializer_class = PersonalTasksSerializer

    def get(self, request, **kwargs):
        year = datetime.today().year
        st = kwargs.get('st', '{}-01-01'.format(year))
        et = kwargs.get('et', datetime.today().strftime('%Y-%m-%d'))
        option = kwargs.get('option', 'activate')
        profile_id = kwargs.get('id', None)
        user = None

        if profile_id is None:
            user = request.user
        else:
            user = User.objects.filter(profile__id=profile_id).first()

        if user == request.user:
            pass
        else:
            if request.user.profile.is_group_leader:
                if request.user.profile.group.id != user.profile.group.id:
                    return Response({'detail': '你没有权限'}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'detail': '你没有权限'}, status=status.HTTP_403_FORBIDDEN)
        qs = user.personal_task.filter(
            start_time__gte=st).filter(start_time__lte=et)
        res = None
        if option == 'all':
            res = qs.all()
        else:
            res = qs.filter(models.Q(status=2) | models.Q(status=3)).all()
        status_code = status.HTTP_200_OK
        s = self.serializer_class(res, many=True)
        return Response(s.data, status_code)


class PersonalTasksCreateView(CreateAPIView):
    permission_classes = (IsAuthenticated, )  # 必须验证授权的用户
    authentication_class = JSONWebTokenAuthentication
    serializer_class = PersonalTasksSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        print(serializer.is_valid(raise_exception=True))
        # 在调用is_valid后才可能调用save()
        serializer.validated_data['worker'] = request.user
        # 如果需要修改is_valid后清洗过的数据必须在.validated_data中修改
        serializer.save()
        response = {
            'success': 'True',
            'status code': status.HTTP_201_CREATED,
            'message': 'Jobs Create Successfully',
            'more': serializer.data
        }
        return Response(response, status.HTTP_201_CREATED)


class ReportListView(ListAPIView):
    permission_classes = (IsAuthenticated, )  # 必须验证授权的用户
    authentication_class = JSONWebTokenAuthentication
    serializer_class = ReportSerializer

    def get(self, request, **kwargs):
        tasks_id = kwargs.get('tasks_id', None)
        userprofile_id = kwargs.get('userprofile_id', None)
        if userprofile_id is None:
            userprofile_id = request.user.profile.id
        else:
            if request.user.profile.is_group_leader:
                if request.user.profile.group.id != Profile.objects.filter(profile__id=userprofile_id).first().group.id:
                    # 是groupleader 并且是相同组
                    return Response({'detail': '你没有权限'}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'detail': '你没有权限'}, status=status.HTTP_403_FORBIDDEN)

        user = User.objects.filter(profile__id=userprofile_id).first()
        if not user:
            return Response({'detail': '用户不存在'}, status.HTTP_400_BAD_REQUEST)
        # TODO 应当根据用户的项目列表返回用户的报告
        rec = Reports.objects.filter(
            tasks__id=tasks_id).filter(tasks__worker=user).all()
        # rec = Reports.objects.all()
        s = self.serializer_class(rec, many=True)
        status_code = status.HTTP_200_OK
        return Response(s.data, status_code)


class ReportCreateView(CreateAPIView):
    permission_classes = (IsAuthenticated, )  # 必须验证授权的用户
    authentication_class = JSONWebTokenAuthentication
    serializer_class = ReportCreateSerializer

    def post(self, request):
        user = request.user
        serializer = self.serializer_class(data=request.data)
        print(serializer.is_valid(raise_exception=True))
        tasks = serializer.validated_data['tasks']
        if tasks.worker_id != user.id:
            return Response({'detail': '你没有创建这个工作任务'}, status.HTTP_400_BAD_REQUEST)
        if 'update_time' not in serializer.validated_data.keys():
            serializer.validated_data['update_time'] = datetime.today().strftime(
                '%Y-%m-%d')
        serializer.save()
        response = {
            'success': 'True',
            'status code': status.HTTP_201_CREATED,
            'message': 'JobReport Create Successfully',
            'more': serializer.data
        }
        return Response(response, status.HTTP_201_CREATED)
