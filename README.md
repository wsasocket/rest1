[reference](https://medium.com/analytics-vidhya/django-rest-api-with-json-web-token-jwt-authentication-69536c01ee18)
本例子使用了标准的创建project和app的方法，所以：
- 1
需要在 settings.py 文件的 INSTALLED_APPS 项目下添加 'medium.apps.MediumConfig',才能使manage.py认识到还有app的名字叫medium

- 2
通过对代码的学习发现，这个例子通过重建一个User模型（继承自Django的原有User模型）并创建一个profile模型完成了自定义设计。实际上对于大多数用户可以考虑通过拓展profile模型，完善你对user模型的个性化需求，实际上就相当于延展了原有的user模型 * OneToOneField *

-3 
Django中JWT的使用机制比较完善，对于扩展用户后如何自定义permision_class也进行演示


本项目用于练手，主要是熟悉Django + RESTFul框架，基本的设计思路如下
用户管理使用django自带的User模型，拓展一对一的Profile模型，主要是将用户归属到某一个自定义的UserGroup中。UserGroup使用初始定义的值，暂时无法通过接口进行增删改。列出UserGroup列表不需要用户登录。
管理组可以设置用户密码，groupleader也可以重置本组成员的密码。
管理组可以设置当前公司的项目清单Project，用户登陆后可以看到清单。
用户、注册登陆后都不是groupleader，这个需要管理员直接在数据库中修改，这部分工作量很小，没必要做专门的接口
用户登录后在http头部就增加一个Authorization: Bearer XXXXXXX...... 的认证信息，这个认证信息(JWT)有时效性，同时内部还包含用户信息。
用户登陆后可以根据当前的Project的清单设置自己的PersonalTasks，这个任务来自于项目，用于方便后续的工作量统计
用户建立的PersonalTasks应当是当前较为明确的工作（细化工作），也就是最近需要完成的任务，这样每天或者每周的报告Report可以不需要写太多。所以可能存在一个项目本分解成多个小的任务的情况。
个人的报告Report是PersonalTasks的详细工作情况，PersonalTasks又是根据公司的当前项目Project的细化分解，通过这个链条关系，可以统计出每个项目耗费的资源情况，也可以统计出每个人在不同项目中的投入情况。（统计部分目前还没有做）