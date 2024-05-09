import random
import time
import urllib
import requests

from http.cookies       import SimpleCookie

requests.packages.urllib3.disable_warnings()


def post_request(session, url, header, post_body, cookies=None, proxy=None):
    resp = session.post(url,
                        headers=header,
                        data=post_body,
                        verify=False,
                        cookies=cookies,
                        )
    printf(f'request: POST, url: {url}, headers: {header}, data: {post_body}, cookies: {cookies}, proxy: {proxy}')
    printf(f'Response code: {resp.status_code}')
    printf(f'Response cookies: {resp.cookies.get_dict()}')
    printf(f'Response headers: {resp.headers}')
    printf(f'Response text: {resp.text}')
    return resp


def get_request(session, url, header, cookies=None, proxy=None):
    resp = session.get(url,
                       headers=header,
                       verify=False,
                       cookies=cookies,
                       )
    printf(f'request: GET, url: {url}, headers: {header}, cookies: {cookies}, proxy: {proxy}')
    printf(f'Response code: {resp.status_code}')
    printf(f'Response cookies: {resp.cookies.get_dict()}')
    printf(f'Response headers: {resp.headers}')
    printf(f'Response text: {resp.text}')
    return resp


def rand_str(length):
    rand = ''
    random_str = '0123456789abcdef'
    for _ in range(length):
        rand += random.choice(random_str)
    return rand


def fix_json(json_string):
    json_string = json_string.replace('"', '\\"')
    json_string = json_string.replace("'", "\"")

    return json_string


def get_trace_id(aid: str, device_id: str):
    timestamp = "%x" % (round(time.time() * 1000) & 0xffffffff)

    if device_id == "":
        device_str = rand_str(16)
    else:
        device_str = hex(int(device_id))[2:]

    aid_str = hex(int(aid))[2:]
    random_str = str(timestamp) + "10" + device_str + rand_str(2) + "0" + aid_str
    trace_id = f"00-{random_str}-{random_str[:16]}-01"
    return trace_id


def to_query_str(query_dict: dict):
    return urllib.parse.urlencode(query_dict)


def printf(text: str, log=False):
    print(text)
    file = 'log.txt'
    if log:
        with open(file, 'a+') as f:
            f.write(f'{text}\n\n')
            f.close()


def cookie_string(json_cookie):
    c_str = "; ".join([f"{key}={value}" for key, value in json_cookie.items()])
    return c_str

def cookie_json(response):
    cookie_string   = response.cookies
    cookies         = SimpleCookie()
    cookies.load(cookie_string)
    cookies_dict    = {key: morsel.value for key, morsel in cookies.items()}
    return cookies_dict
