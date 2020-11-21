from django.shortcuts import render

# Create your views here.
"""
Created on Thu Dec  6 14:04:16 2019
@author: sambhav
"""
from rest_framework import status
from rest_framework.generics import (CreateAPIView, RetrieveAPIView,)
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from .models import UserProfile
from .serializers import (UserRegistrationSerializer, UserLoginSerializer,)


class MyPermissionClass(BasePermission):
    # https://www.django-rest-framework.org/api-guide/permissions/#custom-permissions
    # 创建一个新的 permission 类继承自 rest_framework.permissions.BasePermission
    # 如果是 class 方式 复写 has_permission(self, request, view, obj)  方法
    # 如果是 function 方式 复写 has_object_permission(self, request, view, obj)  方法
    # 在这个函数中对request.user进行逻辑处理 返回合适的True/False
    message = 'Adding customers not allowed.'

    def has_object_permission(self, request, view, obj):
        # function 方式
        print(request)
        if 'gmail' in request.user.email:
            return False
        return True

    def has_permission(self, request, view):
        # class 方式
        print(request)
        if 'gmail' in request.user.email:
            return False
        return True


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
            'email':serializer.data['email'],
            'token': serializer.data['token'],
        }
        status_code = status.HTTP_200_OK

        return Response(response, status=status_code)


class UserProfileView(RetrieveAPIView):

    permission_classes = (IsAuthenticated, )  # 必须验证授权的用户
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
