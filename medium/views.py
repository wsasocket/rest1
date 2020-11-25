from django.shortcuts import render

# Create your views here.
"""
Created on Thu Dec  6 14:04:16 2019
@author: sambhav
"""
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.generics import (CreateAPIView, ListAPIView,
                                     RetrieveAPIView, UpdateAPIView)
from rest_framework.permissions import (AllowAny, BasePermission,
                                        IsAuthenticated)
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from .models import PersonalTasks, Projects, Reports, UserGroup, UserProfile
from .permissions import MustStuffGroupPermission, NeedLeaderPermission
from .serializers import (JobReportSerializer, JobsSerializer,
                          ProjectsSerializer, UserGroupSerializer,
                          UserLoginSerializer, UserProfileSerializer,
                          UserRegistrationSerializer, UserSerializer)


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


class UserProfileView(ListAPIView):

    permission_classes = (IsAuthenticated,)  # 必须验证授权的用户
    authentication_class = JSONWebTokenAuthentication  # 使用这个方法验证授权信息
    serializer_class = UserProfileSerializer

    def get(self, request, **kwargs):
        # 如果有option 参数先验证基本的权限，再根据参数性质进行检索
        option = kwargs.get('option', None)
        if option == 'all':
            if request.user.profile.group.level != 100:
                return Response({'detail': '你不是管理组成员，无权查看所有人员信息'}, status=status.HTTP_403_FORBIDDEN)
            select_users = UserProfile.objects.all()
            s = self.serializer_class(select_users, many=all)
            return Response(s.data, status=status.HTTP_200_OK)
        if option is not None:
            # UUID
            if not request.user.profile.is_group_leader:
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
        if 'id' not in kwarg.keys():
            # 枚举所有的组信息
            groups = UserGroup.objects.all()
            s = self.serializer_class(groups, many=True)
        else:
            # 枚举指定组信息
            groups = UserGroup.objects.filter(id=kwarg['id']).first()
            # 直接将数据库的结果导入到serializer中就能得到完美的结果
            s = self.serializer_class(groups)
        return Response(s.data, status=status.HTTP_200_OK)


class UserGroupViewCreate(CreateAPIView):
    permission_classes = (IsAuthenticated, )  # 必须验证授权的用户
    authentication_class = JSONWebTokenAuthentication  # 使用这个方法验证授权信息
    serializer_class = UserGroupSerializer
    # 增加新的组

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {
            'success': 'True',
            'status code': status.HTTP_201_CREATED,
            'message': 'Group Add successfully',
            'name': serializer.data['name'],
            'level': serializer.data['level'],
        }
        return Response(response, status=status.HTTP_201_CREATED)


class UserGroupViewUpdate(UpdateAPIView):

    permission_classes = (IsAuthenticated, )  # 必须验证授权的用户
    authentication_class = JSONWebTokenAuthentication  # 使用这个方法验证授权信息
    serializer_class = UserGroupSerializer
    # 在 url.py中设置正则名为 一致
    # 就是说通过url设置查询的关键字 ，这个框架自动化的地方在于把 lookup_field queryset
    # 设置好会自动过滤出需要的数据set，在serializer类中可以修改保存
    # lookup_field = 'id'  # 注意在请求url中的正则表达式
    # queryset = UserGroup.objects.all()
    # 修改组的信息

    def patch(self, request, **kwargs):
        instance = UserGroup.objects.filter(id=kwargs['id']).first()
        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {
            'success': 'True',
            'status code': status.HTTP_200_OK,
            'message': 'Group Modify successfully',
            'name': serializer.data['name'],
            'level': serializer.data['level'],
        }
        return Response(response, status=status.HTTP_202_ACCEPTED)


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


class ProjectViewCreate(CreateAPIView):
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


class ProjectViewUpdate(UpdateAPIView):
    pass


class JobListView(ListAPIView):
    permission_classes = (IsAuthenticated, )  # 必须验证授权的用户
    authentication_class = JSONWebTokenAuthentication
    serializer_class = JobsSerializer

    def get(self, request, **kwarg):
        user = request.user
        print(user)
        status_code = status.HTTP_200_OK
        s = self.serializer_class(user.personal_jobs, many=True)
        return Response(s.data, status_code)


class JobCreateView(CreateAPIView):
    permission_classes = (IsAuthenticated, )  # 必须验证授权的用户
    authentication_class = JSONWebTokenAuthentication
    serializer_class = JobsSerializer

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


class JobReportListView(ListAPIView):
    permission_classes = (IsAuthenticated, )  # 必须验证授权的用户
    authentication_class = JSONWebTokenAuthentication
    serializer_class = JobReportSerializer

    def get(self, request, **kwargs):
        job_id = kwargs['job_id']
        user = request.user
        rec = JobItem.objects.filter(jobs__id=job_id).all()
        s = self.serializer_class(rec, many=True)
        status_code = status.HTTP_200_OK
        return Response(s.data, status_code)


class JobReportCreateView(CreateAPIView):
    permission_classes = (IsAuthenticated, )  # 必须验证授权的用户
    authentication_class = JSONWebTokenAuthentication
    serializer_class = JobReportSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        print(serializer.is_valid(raise_exception=True))
        serializer.save()
        response = {
            'success': 'True',
            'status code': status.HTTP_201_CREATED,
            'message': 'JobReport Create Successfully',
            'more': serializer.data
        }
        return Response(response, status.HTTP_201_CREATED)
