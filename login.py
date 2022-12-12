#!user/bin/env python
# -*- coding:utf-8 -*-
"""SEU-Auto-Report-Back:
    自动销假脚本，每日定时检查并销假，支持GitHub Actions在线部署
@File: login.py
@Brief: 使用一卡通号+密码登录ehall，返回登录后的session
@From: https://github.com/luzy99/SEUAutoLogin，有部分改动
@Created Date: 2022/12/10
@Last Modified Date: 2022/12/12
"""

import requests
from bs4 import BeautifulSoup
from encrypt import encryptAES


def login_ehall(id: str, password: str) -> requests.Session:
    """登录ehall，返回登录后的session

    Args:
        id (str): 一卡通号
        password (str): 密码

    Returns:
        requests.Session: 登录后的session
    """
    ss = requests.Session()
    login_data = {'username': id}
    headers = {
        'Content-Type':
        'application/x-www-form-urlencoded',
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
    }
    ss.headers.update(headers)

    #  获取登录页面表单，解析隐藏值
    login_url = 'https://newids.seu.edu.cn/authserver/login?goto=\
        http://my.seu.edu.cn/index.portal'

    try:
        login_res = ss.get(login_url)
    except Exception:
        raise Exception('无法连接到登录页面，请检查网络连接。')

    soup = BeautifulSoup(login_res.text, 'html.parser')
    attrs = soup.select('[tabid="01"] input[type="hidden"]')
    for k in attrs:
        if k.has_attr('name'):
            login_data[str(k['name'])] = str(k['value'])
        elif k.has_attr('id'):
            login_data[str(k['id'])] = str(k['value'])
    login_data['password'] = encryptAES(password,
                                        login_data['pwdDefaultEncryptSalt'])
    login_res = ss.post(login_url, data=login_data)

    # 登录ehall（存在多次302）
    login_res = ss.get(
        'http://ehall.seu.edu.cn/login?service=http://ehall.seu.edu.cn/new/index.html'
    )

    # 获取登录信息（验证结果）
    login_res = ss.get(
        'http://ehall.seu.edu.cn/jsonp/userDesktopInfo.json').json()
    if ('hasLogin' not in login_res) or (login_res['hasLogin'] is False):
        raise Exception('登录失败，请检查配置文件中用户名和密码是否正确。')
    # print(login_res['userName'] + '(' + login_res['userId'] + ')', '登录成功！')
    # 因为GitHub Actions运行结果是任何人可见的，所以不打印姓名学号了
    print('登录成功！')
    return ss
