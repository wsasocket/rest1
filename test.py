
from django.core.wsgi import get_wsgi_application
import json
import requests
from functools import wraps
import pymysql
import os 
import random
# pymysql.version_info = (1, 4, 13, "final", 0)
pymysql.install_as_MySQLdb()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rest.settings')
application = get_wsgi_application()
from medium.models import UserGroup, UserProfile, Projects, PersonalTasks, Reports
from django.contrib.auth.models import User
GROUPS = ('安全组', '管理组', '前端组', '平台组', '网络组', '测试部', '应用组',)
USERS = ({'夏继诚': 'M', '顾耀东': 'M'}, {'苏大强': 'M'}, {
         '王科达': 'M', '杨奎': 'M'}, {'顾邦才': 'M', '杨福朵': 'F'}, {'钟百鸣': 'M', '赵志勇': 'M'}, {'沈青禾': 'F', '顾悦溪': 'F'}, {'杨一学': 'M', '丁放': 'F'},)
AUTH_KEYS = dict()
PASSWORD = dict()


def GET(url, auth_keys=None):
    header = {'Content-Type': 'application/json'}
    if auth_keys:
        header.update({'Authorization': 'Bearer {}'.format(auth_keys)})
    r = requests.get(url, headers=header)
    return (r.status_code, r.text)


def POST(url, data=None, auth_keys=None):
    header = {'Content-Type': 'application/json; charset=utf-8'}
    if auth_keys:
        header.update({'Authorization': 'Bearer {}'.format(auth_keys)})
    r = requests.post(url, headers=header, data=data)
    return (r.status_code, r.text)


def PUT(url, data=None, auth_keys=None):
    header = {'Content-Type': 'application/json'}
    if auth_keys:
        header.update({'Authorization': 'Bearer {}'.format(auth_keys)})
    r = requests.put(url, headers=header, data=data.encode('utf-8'))
    return (r.status_code, r.text)


def clean_database():
    dbs = (UserProfile, Projects, PersonalTasks, Reports, User)
    for db in dbs:
        db.objects.all().delete()

def generate_phone():
    select_a = ['30','31','32','33','34','35','36','37','38','39','89','88','87','86','85','84','83','82','81','80']
    A = select_a[random.randint(0, 19)]
    B = ''.join([str(random.randint(0, 9)) for i in range(10)])
    return f'1{A}{B}'

def generate_passwd():
    lib = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join([lib[random.randint(0, len(lib) - 1)] for i in range(12)])

def generate_email():
    lib = 'abcdefghijklmnopqrstuvwxyz'
    return '{}@gmail.com'.format(''.join([lib[random.randint(0, len(lib) - 1)] for i in range(6)]))

def get_groupid_by_name(groups, name):
    for g in groups:
        if g['name'] == name:
            return g['id']
    return None

if __name__ == "__main__":
    # clean database
    clean_database()
    URL = 'http://127.0.0.1:8000/api/'
    c, t = GET(URL + 'group/')
    groups = None
    if c == 200:
        groups = json.loads(t)
    else:
        print('列出组清单的请求失败')
        exit()
    print('----列出组的清单---')
    list(map(print, groups))
    print('----开始注册用户----')

    for g, u in zip(GROUPS, USERS):
        data = dict()
        for name, gender in u.items():
            data["user"] = dict()
            data['user']["email"] = generate_email()
            data['user']["password"] = generate_passwd()
            PASSWORD[name] = data['user']["password"]
            data['phone_number'] = generate_phone()
            data['group'] = get_groupid_by_name(groups, g)
            data['gender'] = gender
            data['user']["username"] = name
            c, t = POST(URL + 'signup/', data=json.dumps(data))
            if c == 201:
                print(f'{name}注册用户成功')
            else:
                print(f'{name}注册用户失败')

    print('----登录测试1----')
    for name,passwd in PASSWORD.items(): 
        data=dict()
        data["username"]=name
        data["password"]=passwd
        c, t = POST(URL + 'signin/', data=json.dumps(data))
        if c == 200:
            print(f'{name}登录成功')
        else:
            print(f'{name}登录失败')
    print('----登录测试2----')
    for name,passwd in PASSWORD.items(): 
        data=dict()
        data["username"]=name
        data["password"]=passwd+'1'
        c, t = POST(URL + 'signin/', data=json.dumps(data))
        if c == 200:
            print(f'{name}登录成功')
        else:
            print(f'{name}登录失败')