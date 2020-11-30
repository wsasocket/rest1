"""
Created on Thu Dec  6 11:14:00 2019
@author: sambhav
"""
from datetime import datetime

from django.contrib.auth import authenticate
from django.contrib.auth.models import User, update_last_login
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from .models import PersonalTasks, Projects, Reports, UserGroup, UserProfile

# 获取 setting.py 中的定义常量
JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password',
                  'email', 'is_active', 'date_joined', 'last_login')
        extra_kwargs = {'password': {'write_only': True}}


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
                'User with given username and password does not exists'
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
        fields = ['id', 'name', 'level']
        # extra_kwargs = {'id': {'read_only': True}}

    # 创建数据记录
    # def create(self, validated_data):
    #     # 返回 Models的数据
    #     return UserGroup.objects.create(**validated_data)

    # 更新数据记录 使用POST或者PATCH PUT不重要，重要的是要传给这个函数一个instance，否则就会调用create
    # def update(self, instance, validated_data):
    #     # instance 就是数据库查询实例
    #     # instance.id = validated_data.get('id', instance.id)
    #     instance.name = validated_data.get('name', instance.name)
    #     instance.level = validated_data.get('level', instance.level)
    #     instance.save()
    #     return instance


class UserRegistrationSerializer(serializers.ModelSerializer):

    user = UserSerializer(required=False)
    group = serializers.UUIDField(required=False)

    class Meta:
        model = UserProfile
        fields = ('user', 'group', 'phone_number', 'gender', 'group')

    def create(self, validated_data):
        # 从字典中pop出user字段的数据作为生成user需要的数据
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        # 余下的数据用于创建一个用户的profile
        group_instance = UserGroup.objects.filter(
            id=validated_data['group']).first()
        UserProfile.objects.create(
            user=user,
            phone_number=validated_data['phone_number'],
            gender=validated_data['gender'],
            # profile中的外键指向group，只要提交group的pk就能自动获取group实例
            group=group_instance
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    # 两个外键，如果需要详细信息需要增加单独的序列化模型，否则只有pk
    user = UserSerializer()
    group = UserGroupSerializer()
    group.Meta.fields = ('id', 'name', 'level',)

    class Meta:
        model = UserProfile
        fields = ('id', 'user', 'group', "phone_number",
                  'gender', 'is_group_leader')


class PersonalTasksSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalTasks
        # fields = '__all__'
        exclude = ('worker',)  # 这个信息可以从Token中获取

    def create(self, validated_data):
        return PersonalTasks.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.deadline = validated_data.get('deadline', instance.deadline)
        instance.status = validated_data.get('status', instance.status)
        # instance.save()


class UserSetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance


class ReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reports
        exclude = ('update_time',)

    def create(self, validated_data):
        return Reports.objects.create(**validated_data)


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reports
        fields = '__all__'


class ProjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = '__all__'

    def create(self, validated_data):
        return Projects.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.deadline = validated_data.get('deadline', instance.deadline)
