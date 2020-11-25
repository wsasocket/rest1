from rest_framework.permissions import BasePermission


class NeedLeaderPermission(BasePermission):
    # https://www.django-rest-framework.org/api-guide/permissions/#custom-permissions
    # 创建一个新的 permission 类继承自 rest_framework.permissions.BasePermission
    # 如果是 class 方式 复写 has_permission(self, request, view, obj)  方法
    # 如果是 function 方式 复写 has_object_permission(self, request, view, obj)  方法
    # 在这个函数中对request.user进行逻辑处理 返回合适的True/False
    message = '至少是Group Leader才能拥有此权限'
    # def has_object_permission(self, request, view, obj):
    #     # function 方式
    #     print(request)
    #     if 'gmail' in request.user.email:
    #         return False
    #     return True

    def has_permission(self, request, view):
        # class 方式
        print(request)
        if request.user.profile.is_group_leader:
            return True
        return False


class MustStuffGroupPermission(BasePermission):

    message = '必须是管理组成员才能拥有这个权限.'

    def has_permission(self, request, view):
        # class 方式
        print(request)
        return request.user.profile.group.level == 100
