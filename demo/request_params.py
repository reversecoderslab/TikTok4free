from utils import *


def generate_url_common_params(dev_info, extra={}):
    ts = round(time.time() * 1000)
    url_params = {
        "ac": "wifi",
        "ts": ts // 1000,
        "ac2": "wifi5g",
        "aid": dev_info["appId"],
        "dpi": dev_info["densityDpi"],
        "iid": dev_info["installId"],
        "uoo": "1",
        "cdid": dev_info["cdid"],
        "locale": dev_info["language"],
        "ssmix": "a",
        "region": dev_info["region"],
        "os_api": str(dev_info["apiLevel"]),
        "channel": dev_info["channel"],
        "_rticket": ts,
        "app_type": "normal",
        "host_abi": dev_info["cpuAbi"],
        "language": dev_info["language"],
        "app_name": dev_info["appName"],
        "openudid": dev_info["openUdid"],
        "device_id": dev_info["deviceId"],
        "op_region": dev_info["region"],
        "ab_version": dev_info["appVersion"],
        "os_version": dev_info["osVersion"],
        "resolution": f'{dev_info["screenHeight"]}*{dev_info["screenWidth"]}',
        "sys_region": dev_info["region"],
        "fake_region": dev_info["region"],
        "app_language": dev_info["language"],
        "build_number": dev_info["appVersion"],
        "device_type": dev_info["deviceModel"],
        "device_brand": dev_info["deviceBrand"],
        "version_code": dev_info["appVersionCode"],
        "version_name": dev_info["appVersion"],
        "timezone_name": dev_info["timezoneName"],
        "carrier_region": dev_info["carrierRegion"],
        "device_platform": "android",
        "timezone_offset": dev_info["timezoneOffset"],
        "update_version_code": str(dev_info["updateVersionCode"]),
        "manifest_version_code": str(dev_info["manifestVersionCode"]),
    }
    return urllib.parse.urlencode(url_params | extra)


def generate_common_header_info(dev_info):
    return {
        'sdk-version': '2',
        'user-agent': dev_info["userAgent"],
        'x-vc-bdturing-sdk-version': '2.2.0',
        'x-tt-dm-status': 'login=1;ct=1;rt=1',
        'passport-sdk-version': '5.12.1',
        'x-bd-kmsv': '0',
        'x-ss-dp': dev_info["appId"],
        'x-tt-trace-id': get_trace_id(dev_info["appId"], dev_info["deviceId"]),
        'accept-encoding': 'gzip, deflate',
    }
