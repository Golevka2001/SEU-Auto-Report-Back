#!user/bin/env python
# -*- coding:utf-8 -*-
"""SEU-Auto-Report-Back:
    自动销假脚本，每日定时检查并销假，支持GitHub Actions在线部署
@File: report_back.py
@Brief: 调用login.py登录后进行销假
@Author: Golevka2001<gol3vka@163.com>
@Created Date: 2022/12/10
@Last Modified Date: 2022/12/12
"""

import json
import os
from datetime import datetime

import requests
from login import login_ehall


def report_back(ss: requests.Session, id: str, is_ug: bool) -> None:
    """销假

    Args:
        ss (requests.Session): 登录ehall后返回的session
        id (str): 一卡通号
        is_ug (bool): 是否为本科生
    """
    req_data = {'XSBH': id, 'pageSize': '1', 'pageNumber': '1'}
    if is_ug:
        print('本科生组')
        # 本科生出校登记审批页面：
        ss.get('http://ehall.seu.edu.cn/appShow?appId=4810794463325921')
        res = ss.post(
            'http://ehall.seu.edu.cn/xsfw/sys/xsqjapp/modules/wdqj/wdqjbg.do',
            data=req_data)
    else:
        print('研究生组')
        # 研究生出校登记审批页面：
        ss.get('http://ehall.seu.edu.cn/appShow?appId=5869188708264821')
        res = ss.post(
            'http://ehall.seu.edu.cn/ygfw/sys/xsqjappseuyangong/modules/wdqj/wdqjbg.do',
            data=req_data)

    if res.status_code == 403:
        raise Exception('登录信息失效或本/研组别设置错误，请检查配置文件undergraduate字段是否正确。')

    res = res.json()
    # datas是什么东西...回去学英语去！
    if (res['datas']['wdqjbg']['totalSize'] == 0) or ('datas' not in res):
        raise Exception('获取数据失败')

    # 获取最新的一条数据：
    if res['datas']['wdqjbg']['rows'][0]['XJZT_DISPLAY'] == '已销假':
        print('无需销假')
        return

    # 销假：
    if is_ug:
        # FIXME: 不知道怎么解决这个东西，是个form-data的参数，各种方法都试了，只有传字符串有效，很怪，下面那个也是一样
        # report_data = {'SQBH': res['datas']['wdqjbg']['rows'][0]['SQBH']}
        report_data = 'requestParamStr={"SQBH":"%s"}' % (
            res['datas']['wdqjbg']['rows'][0]['SQBH'])
        res = ss.post(
            'http://ehall.seu.edu.cn/xsfw/sys/xsqjapp/modules/xjset/xjshApply.do',
            data=report_data.encode('utf-8')).json()
    else:
        # FIXME: 和上面一样的怪东西，没招了
        # report_data = {
        #     'SQBH': res['datas']['wdqjbg']['rows'][0]['SQBH'],
        #     'XSBH': res['datas']['wdqjbg']['rows'][0]['XSBH'],
        #     'SHZT': res['datas']['wdqjbg']['rows'][0]['SHZT'],
        #     'XJFS': "2",
        #     'XJSJ': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        #     'XJRQ': datetime.now().strftime('%Y-%m-%d'),
        #     'SQR': res['datas']['wdqjbg']['rows'][0]['XSBH'],
        #     'SQRXM': res['datas']['wdqjbg']['rows'][0]['XM'],
        #     'THZT': res['datas']['wdqjbg']['rows'][0]['THZT']
        # }
        report_data = 'data={"SQBH":"%s","XSBH":"%s","SHZT":"%s","XJFS":"2","XJSJ":"%s","XJRQ":"%s","SQR":"%s","SQRXM":"%s","THZT":"%s"}' % (
            res['datas']['wdqjbg']['rows'][0]['SQBH'],
            res['datas']['wdqjbg']['rows'][0]['XSBH'],
            res['datas']['wdqjbg']['rows'][0]['SHZT'],
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            datetime.now().strftime('%Y-%m-%d'),
            res['datas']['wdqjbg']['rows'][0]['XSBH'],
            res['datas']['wdqjbg']['rows'][0]['XM'],
            res['datas']['wdqjbg']['rows'][0]['THZT'])
        res = ss.post(
            'http://ehall.seu.edu.cn/ygfw/sys/xsqjappseuyangong/modules/leaveApply/addXjApply.do',
            data=report_data.encode('utf-8')).json()  # 姓名中含中文，必须utf-8

    # print(res)
    if res['returnCode'] != '#E000000000000':
        # 或者 res['description'] != '成功'
        raise Exception('销假失败')
    print('销假成功')


if __name__ == '__main__':
    """
    当前使用GitHub Actions在线部署，无需使用config.json写入个人信息。
    如果需要在本地运行，自行修改以下注释部分，将参数改为从配置文件读取，并编辑配置文件。
    """

    # # 读取配置文件：
    # with open('config.json', 'r', encoding='utf-8') as f:
    #     config = json.load(f)

    # 读取环境变量：
    id = os.environ['ID']
    password = os.environ['PASSWORD']
    if os.environ['IS_UG'] == 'true':
        is_ug = True
    else:
        is_ug = False

    # 登录：
    try:
        # ss = login_ehall(config['id'], config['password'])
        ss = login_ehall(id, password)
    except Exception as e:
        print(e)
        exit(-1)

    # 销假：
    try:
        # report_back(ss, config['id'], config['undergraduate'])
        report_back(ss, id, is_ug)
    except Exception as e:
        print(e)
        exit(-1)
