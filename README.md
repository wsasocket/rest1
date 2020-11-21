[reference](https://medium.com/analytics-vidhya/django-rest-api-with-json-web-token-jwt-authentication-69536c01ee18)
本例子使用了标准的创建project和app的方法，所以：
- 1
需要在 settings.py 文件的 INSTALLED_APPS 项目下添加 'medium.apps.MediumConfig',才能使manage.py认识到还有app的名字叫medium

- 2
通过对代码的学习发现，这个例子通过重建一个User模型（继承自Django的原有User模型）并创建一个profile模型完成了自定义设计。实际上对于大多数用户可以考虑通过拓展profile模型，完善你对user模型的个性化需求，实际上就相当于延展了原有的user模型 * OneToOneField *

-3 
Django中JWT的使用机制比较完善，对于扩展用户后如何自定义permision_class也进行演示