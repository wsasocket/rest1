# Create your models here.
"""
Created on Thu Dec  5 10:04:16 2019
@author: sambhav
"""

import uuid

# 继承使用 Django自带的user模型和模型管理类，
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin, User)
from django.db import models


class UserGroup(models.Model):
    # 用户分组
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

    phone_number = models.CharField(
        max_length=13, unique=True, null=False, blank=False)
    age = models.PositiveIntegerField(null=False, blank=False)
    GENDER_CHOICES = (
        ('M', '高富帅'),
        ('F', '白富美'),
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    # groupleader有权查看本组人员的工作报告并审核
    is_group_leader = models.BooleanField(default=False)

    class Meta:
        '''
        自定义在数据库中的表名
        '''
        db_table = "profile"


class Projects(models.Model):
    # 项目
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status_choices = ((1, '立项'), (2, '启动'), (3, '暂停'), (4, '完成'), (5, '废弃'),)
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=256)
    start_time = models.DateField(null=True)
    deadline = models.DateField(null=True)
    status = models.IntegerField(choices=status_choices)

    @classmethod
    def get_members(cls):
        return cls.project.worker

    class Meta:
        db_table = "projects"


class Jobs(models.Model):
    # 每人的工作
    status_choices = ((2, '启动'), (3, '暂停'), (4, '完成'), (5, '废弃'))
    # 这个状态仅仅与是自己工作内容相关，与project无关
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    worker = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='personal_jobs')
    project = models.ForeignKey(
        Projects, on_delete=models.CASCADE, related_name='project_relate_jobs')
    brief = models.CharField(max_length=256, blank=False)
    start_time = models.DateField(null=True)
    deadline = models.DateField(null=True)
    status = models.IntegerField(choices=status_choices)

    class Meta:
        db_table = "jobs"


class JobItem(models.Model):
    # 工作的详细报告
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    jobs = models.ForeignKey(
        Jobs, on_delete=models.CASCADE, related_name='report')
    description = models.CharField(max_length=512, blank=False)
    update_time = models.DateField(null=False)
    audit = models.BooleanField(default=False)
    hours = models.DecimalField(null=False, max_digits=5, decimal_places=1)

    class Meta:
        db_table = "jobitem"
