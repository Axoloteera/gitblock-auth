import requests
import json
import random
import time
import hashlib

config = json.load(open('config.json', encoding='utf-8'))
if config['debug']:
    config = json.load(open('dev-config.json', encoding='utf-8'))
authkey_list = {}
session = requests.Session()
headers = {
    "Accept": "*/*", "Accept-Encoding": "gzip, deflate, br", "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive", "Host": "gitblock.cn", "Origin": "https://gitblock.cn",
    "Referer": "https://gitblock.cn/",
    "Sec-Ch-Ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    "Sec-Ch-Ua-Mobile": "?0", "Sec-Ch-Ua-Platform": '"Windows"', "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
}
security_salt = "DUE$DEHFYE(YRUEHD*&"
last_login_time = -1


def generate_authkey() -> str:
    authkey_list[
        authkey := f"authkey_{''.join(random.sample('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890', 8))}"] = time.time()
    return authkey


def check_authkey(authkey: str) -> bool:
    if authkey in authkey_list:
        if time.time() - authkey_list[authkey] < 60:
            return True
    else:
        return False


def login() -> bool:
    data = {
        "username": (username := config['account']['username']),
        "password": (password := config['account']['password']),
        "t": (timestamp := round(time.time() * 1000) + 2592030000),
        "s": hashlib.sha1(
            f"/WebApi/Users/Login?username={username}&password={password}{security_salt}&t={timestamp}".encode(
                'utf-8')).hexdigest()
    }
    response = session.post("https://gitblock.cn/WebApi/Users/Login", headers=headers, data=data)
    last_login_time = time.time()
    if response.status_code == 200 and str(response.json()['loggedInUser']['id']) == config['account']['userid']:
        return True
    else:
        return False


def clear_authkey() -> None:
    for authkey in list(authkey_list.keys()):
        if time.time() - authkey_list[authkey] > 60:
            del authkey_list[authkey]


def verify(authkey: str) -> dict:
    if check_authkey(authkey):
        req = session.post("https://gitblock.cn/WebApi/Comment/GetPage", headers=headers,
                           data={"forType": "User", "forId": config['account']['userid'], "pageIndex": "1",
                                 "scrollToCommentId": ""}).json()
        if req['pagedThreads']['items'] == []:  # 这代表cookie失效
            if time.time() - last_login_time > 600:
                if login():
                    req = session.post("https://gitblock.cn/WebApi/Comment/GetPage", headers=headers,
                                       data={"forType": "User", "forId": config['account']['userid'], "pageIndex": "1",
                                             "scrollToCommentId": ""}).json()
                else:
                    return {"code": 500}  # code代表错误代码 500代表服务端出现错误
            else:
                return {"code": 500}

        for i in req['pagedThreads']['items']:
            if i['content'] == authkey:
                del authkey_list[authkey]
                return {"code": 200, 'userInfo': req['userMap'][str(i['creatorId'])]}
        return {"code": 404}  # code代表错误代码 201表示没有该authkey

    else:
        return {"code": 404}  # vaild代表该请求无效 code代表错误代码 403代表没有该authkey 例如为超时


if __name__ == '__main__':
    print("请不要直接运行此文件，这是一个模块文件，你可以使用main.py来运行此程序")
