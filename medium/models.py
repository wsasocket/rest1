# Create your models here.
"""
Created on Thu Dec  5 10:04:16 2019
@author: sambhav
"""

import uuid

# 继承使用 Django自带的user模型和模型管理类，
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import PermissionsMixin

# class UserManager(BaseUserManager):
#     '''
#     creating a manager for a custom user model
#     https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#writing-a-manager-for-a-custom-user-model
#     https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#a-full-example
#     '''
#     # 完备 BaseUserManager接口，和使用控制台与 WEB很类似，似乎没有增加更多的逻辑

#     def create_user(self, email, password=None):
#         """
#         Create and return a `User` with an email, username and password.
#         """
#         if not email:
#             raise ValueError('Users Must Have an email address')

#         user = self.model(
#             email=self.normalize_email(email),
#         )
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, email, password):
#         """
#         Create and return a `User` with superuser (admin) permissions.
#         """
#         if password is None:
#             raise TypeError('Superusers must have a password.')

#         user = self.create_user(email, password)
#         user.is_superuser = True
#         user.is_staff = True
#         user.save()

#         return user


# class User(AbstractBaseUser, PermissionsMixin):
#     # 自定义的 User 模型与原来的差不多，仅仅是 id 由自动增量变成了 uuid
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     email = models.EmailField(
#         verbose_name='email address',
#         max_length=255,
#         unique=True
#     )
#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)
#     is_superuser = models.BooleanField(default=False)
#     # 上面都是原有的抽象类定义的字段
#     # TODO: 下面这两个常量的含义不太明确
#     USERNAME_FIELD = 'email'  # 文档说这个变量的含义是用 email 当作 username 进行登录
#     REQUIRED_FIELDS = []

#     # Tells Django that the UserManager class defined above should manage
#     # objects of this type. 这里的 objects 就是数据不操作的那个 objects
#     objects = UserManager()

#     def __str__(self):
#         return self.email

#     class Meta:
#         '''
#         自定义在数据库中的表名
#         '''
#         db_table = "login"

class UserGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, unique=True)
    level = models.IntegerField(unique=True)

    @classmethod
    def get_members(cls):
        pass

    class Meta:
        '''
        自定义在数据库中的表名
        '''
        db_table = "usergroup"


class UserProfile(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # 设置了一个外键，与 User模型相关联 pk相关联
    #  注意 User 模型来自于哪里！
    # related_name 相当于使用user.profile就能访问profile表
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')
    # 一对多关系
    group = models.ForeignKey(
        UserGroup, on_delete=models.CASCADE, related_name='group')

    # first_name = models.CharField(max_length=50, unique=False)
    # last_name = models.CharField(max_length=50, unique=False)
    phone_number = models.CharField(
        max_length=10, unique=True, null=False, blank=False)
    age = models.PositiveIntegerField(null=False, blank=False)
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    is_group_leader = models.BooleanField(default=False)

    class Meta:
        '''
        自定义在数据库中的表名
        '''
        db_table = "profile"


class Projects(models.Model):
    # 项目
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status_choices = ((1, '立项'), (2, '启动'), (3, '暂停'), (4, '完成'),)
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=256)
    start_time = models.DateField(null=True)
    deadline = models.DateField(null=True)
    status = models.IntegerField(choices=status_choices)

    @classmethod
    def get_members(cls):
        return Jobs.objects.filter(project=cls).all()

    class Meta:
        db_table = "projects"


class Jobs(models.Model):
    # 每人的工作
    status_choices = ((2, '启动'), (3, '暂停'), (4, '完成'),)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    worker = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='worker')
    project = models.ForeignKey(
        Projects, on_delete=models.CASCADE, related_name='project')

    brief = models.CharField(max_length=256, blank=False)
    description = models.CharField(max_length=512, blank=False)
    start_time = models.DateField(null=True)
    update_time = models.DateField(null=False)
    deadline = models.DateField(null=True)
    status = models.IntegerField(choices=status_choices)
    hours = models.DecimalField(null=False, max_digits=5, decimal_places=1)

    class Meta:
        db_table = "jobs"
