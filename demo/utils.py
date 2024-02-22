import random
import time
import urllib

import requests

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

def mssdk_id_str():
    return f"b{gen_rnd()}{gen_rnd()}ed{gen_rnd()}{gen_rnd()}{gen_rnd()}-0e0b-{gen_rnd()}{gen_rnd()}{gen_rnd()}a-b{gen_rnd()}c{gen_rnd()}-{gen_rnd()}{gen_rnd()}{gen_rnd()}d{gen_rnd()}af{gen_rnd()}fcaf"

def gen_rnd():
    return random.randint(0,9)

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


def cookie_to_str(cookies, headers=None) -> str:
    _cookies = {}
    if headers:
        for x in headers:
            if x.lower() == "cookie":
                data = headers[x].split(";")
                for x in data:
                    if x.strip() != "":
                        cookie = x.strip().split("=")
                        _cookies[cookie[0]] = cookie[1]

    sess_dict = cookies
    for imn in sess_dict:
        _cookies[str(imn)] = str(sess_dict[imn])

    new_cookies = []
    for x in _cookies:
        new_cookies.append(x + "=" + _cookies[x])

    return "; ".join(new_cookies)
