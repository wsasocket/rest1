"""
Created on Thu Dec  6 11:14:00 2019
@author: sambhav
"""
from datetime import datetime

from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from .models import JobItem, Jobs, Projects, User, UserGroup, UserProfile

# 获取 setting.py 中的定义常量
JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ('phone_number', 'age', 'gender', 'group')


class UserRegistrationSerializer(serializers.ModelSerializer):

    profile = UserSerializer(required=False)

    class Meta:
        model = User
        fields = ('email', 'password', 'profile', 'username', 'is_active',
                  'is_staff', 'first_name', 'last_name')
        # 设置 password的更多参数，write_only 表示输入（写入数据），不能输出
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
            gender=profile_data['gender'],
            # profile中的外键指向group，只要提交group的pk就能自动获取group实例
            group=profile_data['group']
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
            # 自定义的结构，不是从Models派生出来的
            'username': user.get_username(),
            'token': jwt_token,
            'email': user.email,
        }


class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGroup
        fields = '__all__'

    # 创建数据记录
    def create(self, validated_data):
        # 返回 Models的数据
        return UserGroup.objects.create(**validated_data)

    # 更新数据记录 使用POST或者PATCH PUT不重要，重要的是要传给这个函数一个instance，否则就会调用create
    def update(self, instance, validated_data):
        # instance 就是数据库查询实例
        # instance.id = validated_data.get('id', instance.id)
        instance.name = validated_data.get('name', instance.name)
        instance.level = validated_data.get('level', instance.level)
        instance.save()
        return instance


class JobsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Jobs
        fields = '__all__'

    def create(self, validated_data):
        return Jobs.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.deadline = validated_data.get('deadline', instance.deadline)
        instance.status = validated_data.get('status', instance.status)

        instance.description = instance.description + \
            validated_data.get('description', '')
        instance.hours = validated_data.get('hours', instance.hours)
        instance.update_time = validated_data.get(
            'update_time', datetime.today())


class JobReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobItem
        fields = '__all__'

    def create(self, validated_data):
        return JobItem.objects.create(**validated_data)


class ProjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = '__all__'

    def create(self, validated_data):
        return Projects.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.deadline = validated_data.get('deadline', instance.deadline)
