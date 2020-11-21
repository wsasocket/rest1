"""
Created on Thu Dec  6 11:14:00 2019
@author: sambhav
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework_jwt.settings import api_settings
from .models import User, UserProfile

# 获取 setting.py 中的定义常量
JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ('phone_number', 'age', 'gender')


class UserRegistrationSerializer(serializers.ModelSerializer):

    profile = UserSerializer(required=False)

    class Meta:
        model = User
        fields = ('email', 'password', 'profile', 'username', 'is_active',
                  'is_staff', 'first_name', 'last_name')
        # 设置 password的更多参数
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # 从字典中pop出profile字段的数据作为生成profile需要的数据
        profile_data = validated_data.pop('profile')
        # pop profile后的数据用于创建一个用户
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(
            user=user,
            # first_name=profile_data['first_name'],
            # last_name=profile_data['last_name'],
            phone_number=profile_data['phone_number'],
            age=profile_data['age'],
            gender=profile_data['gender']
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    # 定义输出/入json的字段的模型 如果不定义，输入参数无法获取，输出会异常
    # read_only=True 输出
    # write_only=True 输入
    email = serializers.CharField(max_length=255, read_only=True)
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        # 自定义验证函数
        username = data.get("username", None)
        password = data.get("password", None)
        print(username, password)
        # 使用了django自带的验证程序
        user = authenticate(username=username, password=password)
        # 验证正确会返回 模型 User实例
        if user is None:
            # 验证未通过
            raise serializers.ValidationError(
                'A user with this username and password is not found.'
            )
        try:
            # 根据User实例内容创建 token 的 payload
            payload = JWT_PAYLOAD_HANDLER(user)
            # 创建 Token
            jwt_token = JWT_ENCODE_HANDLER(payload)
            update_last_login(None, user)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'User with given email and password does not exists'
            )
        return {
            'username': user.get_username(),
            'token': jwt_token,
            'email': user.email,
        }
