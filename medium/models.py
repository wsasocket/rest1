# Create your models here.
import uuid

# 继承使用 Django自带的user模型和模型管理类，
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin, User)
from django.db import models


class UserGroup(models.Model):
    # 用户分组，组信息可以设置好后直接导入
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # 用户组名称
    name = models.CharField(max_length=128, unique=True)
    # 用户组级别，目前为了简化逻辑，分为两个级别的组，管理组和工作组，管理组的level设定为100，其他为1
    level = models.IntegerField()

    class Meta:
        # 自定义在数据库中的表名
        db_table = "UserGroup"


class UserProfile(models.Model):
    # 用户的详细信息，由于使用原生的User模型，不足的信息用这部分补充，建立one_to_One的关联
    GENDER_CHOICES = (('M', '高富帅'), ('F', '白富美'),)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # 设置了一个外键，与 User模型相关联 pk相关联
    phone_number = models.CharField(
        max_length=13, unique=True, null=False, blank=False)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    # group leader有权查看本组人员的工作报告并审核
    is_group_leader = models.BooleanField(default=False)
    # 与原生的User模型一一对应关联
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')
    # 一个用户必然要归属于一个组，一对多关系
    group = models.ForeignKey(
        UserGroup, on_delete=models.CASCADE, related_name='user_profile')

    class Meta:
        db_table = "UserProfile"


class Projects(models.Model):
    # 公司安排的项目，下面的所有内容仅仅是任务分解的依据，
    # 与分解的任务和状态没有关系
    status_choices = ((1, '立项'), (2, '启动'), (3, '暂停'), (4, '完成'), (5, '废弃'),)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # 项目名称
    name = models.CharField(max_length=128, unique=True)
    # 项目描述
    description = models.CharField(max_length=256)
    # 开始时间
    start_time = models.DateField(null=True)
    # 计划完成时间
    deadline = models.DateField(null=True)
    # 当前项目状态
    status = models.IntegerField(choices=status_choices)

    class Meta:
        db_table = "Projects"


class PersonalTasks(models.Model):
    # 每人的工作项目
    status_choices = ((2, '启动'), (3, '暂停'), (4, '完成'), (5, '废弃'))
    # 这个状态仅仅与是自己工作内容相关，与project无关
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # 任务简介
    brief = models.CharField(max_length=256, blank=False)
    # 任务开始时间，可以为空
    start_time = models.DateField(null=False)
    # 目标完成时间，可以为空
    deadline = models.DateField(null=True)
    # 当前状态
    status = models.IntegerField(choices=status_choices)
    # 完成这项任务的人，从User的角度看就是个人的任务
    worker = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='personal_task')
    # 这项任务所属的项目，从项目角度看就是项目被分解出来的不同任务
    project = models.ForeignKey(
        Projects, on_delete=models.CASCADE, related_name='project_relate_task')

    class Meta:
        db_table = "PersonalTasks"


class Reports(models.Model):
    # 任务的详细报告
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # report的重点内容
    description = models.CharField(max_length=512, blank=False)
    # 更新时间，方便按时间统计
    update_time = models.DateField(null=False)
    # 如果是group leader可以审核成员的每一份报告，审核后不能修改
    audit = models.BooleanField(default=False)
    # 当前report消耗的时间，按照任务或者项目统计，可以统计出资源投入
    hours = models.DecimalField(null=False, max_digits=5, decimal_places=1)
    # report相关联的任务，从任务角度看就是 task_report
    tasks = models.ForeignKey(
        PersonalTasks, on_delete=models.CASCADE, related_name='task_report')

    class Meta:
        db_table = "Report"
