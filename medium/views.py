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

from .models import JobItem, Jobs, Projects, UserGroup, UserProfile
from .permissions import MustStuffGroupPermission, NeedLeaderPermission
from .serializers import (JobReportSerializer, JobsSerializer,
                          ProjectsSerializer, UserGroupSerializer,
                          UserLoginSerializer, UserRegistrationSerializer)


class UserRegistrationView(CreateAPIView):

    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny,)  # 允许所有访问

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        status_code = status.HTTP_201_CREATED
        response = {
            'success': 'True',
            'status code': status_code,
            'message': 'User registered  successfully',
        }

        return Response(response, status=status_code)


class UserLoginView(RetrieveAPIView):

    permission_classes = (AllowAny,)
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = {
            'success': 'True',
            'status code': status.HTTP_200_OK,
            'message': 'User logged in  successfully',
            'name': serializer.data['username'],
            'email': serializer.data['email'],
            'token': serializer.data['token'],
        }
        status_code = status.HTTP_200_OK

        return Response(response, status=status_code)


class UserProfileView(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)  # 必须验证授权的用户
    authentication_class = JSONWebTokenAuthentication  # 使用这个方法验证授权信息

    def get(self, request):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            status_code = status.HTTP_200_OK
            response = {
                'success': 'true',
                'status code': status_code,
                'message': 'User profile fetched successfully',
                'data': [{
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    'phone_number': user_profile.phone_number,
                    'age': user_profile.age,
                    'gender': user_profile.gender,
                    'group': user_profile.group.name
                }]
            }

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
    permission_classes = (IsAuthenticated, )  # 必须验证授权的用户
    authentication_class = JSONWebTokenAuthentication  # 使用这个方法验证授权信息
    serializer_class = UserGroupSerializer
    # 枚举所有的组信息

    def get(self, request, **kwarg):
        # name = request.query_params.get('name', None)

        if 'id' not in kwarg.keys():
            groups = UserGroup.objects.all()
            s = self.serializer_class(groups, many=True)
        else:
            groups = UserGroup.objects.filter(id=kwarg['id']).first()
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
