import base64
import json
import time

import requests

from key import rapidapi_key
from utils import fix_json, printf

rapidapi_server_domain = "tiktok4free.p.rapidapi.com"
rapidapi_server_host = f"https://{rapidapi_server_domain}"


def get_api_common_params(endpoint):
    if len(rapidapi_key) > 0:
        url = f"{rapidapi_server_host}/{endpoint}"
        payload = {}
        headers = {
            "X-RapidAPI-Key": rapidapi_key,
            "X-RapidAPI-Host": rapidapi_server_domain,
            'Content-Type': 'application/json',
        }
    else:
        raise Exception("Please enter a valid api key")
    return url, payload, headers


def do_get_dev_tmpl():
    url, payload, headers = get_api_common_params("get_device_template")
    payload = json.dumps(payload | {
        "platform": 'android'
    })
    response = requests.request("POST", url, headers=headers, data=payload)

    time.sleep(1)

    device_data_base64 = json.loads(response.text)["data"]
    device_data = base64.b64decode(device_data_base64).decode('utf-8')
    return json.loads(fix_json(device_data))


def gen_locals(proxy: str = None):
    url, payload, headers = get_api_common_params("get_locals_from_proxy")
    payload = json.dumps(payload | {
        "proxy": proxy if proxy else ''
    })
    response = requests.request("POST", url, headers=headers, data=payload)

    time.sleep(1)

    return json.loads(response.text)


def get_device_register_body(dev_info):
    url, payload, headers = get_api_common_params("get_device_register_body")
    payload = json.dumps(payload | {
        "dev_info": dev_info
    })
    response = requests.request("POST", url, headers=headers, data=payload)
    time.sleep(1)

    data = json.loads(response.text)["data"]
    printf(f"Device register body: {data}")
    return data


def do_sign_v5(dev_info, timestamp: int, req_url: str, body=None):
    """
    Mobile sign
    :param dev_info
    :param timestamp
    :param req_url
    :param body  required when req_type = "POST"
    :return x_ladon, x_argus, x_gorgon, x_khronos
    """

    req_body = ''
    if body is not None:
        if isinstance(body, (bytes, bytearray)):
            req_body = base64.b64encode(body).decode('utf-8')
        else:
            req_body = base64.b64encode(body.encode('utf-8')).decode('utf-8')

    url, payload, headers = get_api_common_params("get_sign")
    payload = json.dumps(payload | {
        "params": req_url,
        "timestamp": timestamp,
        "payload": req_body,
        "dev_info": dev_info
    })
    printf(f'Sign payload: {payload}')

    response = requests.post(url, headers=headers, data=payload)
    printf(f'Sign response: {response.text}')

    time.sleep(1)

    if response.status_code == 200:
        obj = json.loads(response.text)
        data = obj["data"]
        return data["X-Ladon"], data["X-Argus"], data["X-Gorgon"], data["X-Khronos"], data["X-SS-Stub"]


def encrypt_get_token(dev_info):
    url, payload, headers = get_api_common_params("encrypt_get_token")
    payload = json.dumps(payload | {
        "dev_info": dev_info
    })
    printf(payload)
    response = requests.request("POST", url, headers=headers, data=payload)
    printf(response.text)
    time.sleep(1)

    if response.status_code == 200:
        obj = json.loads(response.text)
        data = obj["data"]
        return base64.b64decode(data)


def encrypt_get_seed(dev_info):
    url, payload, headers = get_api_common_params("get_seed_body")
    payload = json.dumps(payload | {
        "dev_info": dev_info
    })
    printf(payload)
    response = requests.request("POST", url, headers=headers, data=payload)
    printf(response.text)
    time.sleep(1)

    if response.status_code == 200:
        obj = json.loads(response.text)
        data = obj["data"]
        printf(f'Token body: {data}')
        return base64.b64decode(data)


def encrypt_get_report(dev_info):
    url, payload, headers = get_api_common_params("get_ri_report_body")
    payload = json.dumps(payload | {
        "dev_info": dev_info
    })
    printf(payload)
    response = requests.request("POST", url, headers=headers, data=payload)
    printf(response.text)
    time.sleep(1)

    if response.status_code == 200:
        obj = json.loads(response.text)
        data = obj["data"]
        printf(f'Report body: {data}')
        return base64.b64decode(data)


def decrypt_get_token(platform, aid, data):
    url, payload, headers = get_api_common_params("decrypt_get_token")
    payload = json.dumps(payload | {
        "platform": platform,
        "aid": aid,
        "data": base64.b64encode(data).decode('utf-8')
    })
    printf(payload)
    response = requests.request("POST", url, headers=headers, data=payload)
    printf(response.text)
    time.sleep(1)

    if response.status_code == 200:
        obj = json.loads(response.text)
        return obj["data"]


def decrypt_get_seed(platform, aid, data):
    url, payload, headers = get_api_common_params("decrypt_get_seed")
    payload = json.dumps(payload | {
        "platform": platform,
        "aid": aid,
        "data": data
    })
    printf(payload)
    response = requests.request("POST", url, headers=headers, data=payload)
    printf(response.text)
    time.sleep(1)

    if response.status_code == 200:
        obj = json.loads(response.text)
        return obj
