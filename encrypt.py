#!user/bin/env python
# -*- coding:utf-8 -*-
"""SEU-Auto-Report-Back:
    自动销假脚本，每日定时检查并销假
@File: encrypt.py
@Brief: 登录过程中需要对密码进行加密，调用encrypt.js
@From: https://github.com/luzy99/SEUAutoLogin，有部分改动
@Created Date: 2022/12/10
@Last Modified Date: 2022/12/10
"""

import js2py

js_obj = js2py.EvalJs()

with open("./encrypt.js") as f:
    js_content = f.read()


def encryptAES(plain_text, salt):
    # 执行整段JS代码
    js_obj.execute(js_content)
    cipher = js_obj.encryptAES(plain_text, salt)
    # print("加密结果：", cipher)
    return cipher
