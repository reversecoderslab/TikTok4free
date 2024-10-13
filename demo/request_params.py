from utils      import *


def generate_url_common_params(dev_info, extra={}):
    ts = round(time.time() * 1000)
    url_params = {
        'ac': 'wifi',
        'channel': dev_info['app']['channel'],
        'aid': dev_info['app']['appId'],
        'app_name': dev_info['app']['appName'],
        'version_code': dev_info['app']['appVersionCode'],
        'version_name': dev_info['app']['appVersion'],
        'device_platform': 'android',
        'os': 'android',
        'ab_version': dev_info['app']['appVersion'],
        'ssmix': 'a',
        'device_type': dev_info['device']['deviceType'],
        'device_brand': dev_info['device']['deviceBrand'],
        'language': 'en',
        'os_api': dev_info['device']['apiLevel'],
        'os_version': dev_info['device']['osVersion'],
        'openudid': dev_info['device']['openUdid'],
        'manifest_version_code': dev_info['app']['manifestVersionCode'],
        'resolution': f"{dev_info['device']['screenHeight']}*{dev_info['device']['screenWidth']}",
        'dpi': str(dev_info['device']['densityDpi']),
        'update_version_code': str(dev_info['app']['updateVersionCode']),
        '_rticket': ts,
        'is_pad': '0',
        'app_type': 'normal',
        'sys_region': dev_info['geo']['region'],
        'mcc_mnc': dev_info['geo']['mcc_mnc'],
        'timezone_name': dev_info['geo']['timezoneName'],
        'carrier_region_v2': dev_info['geo']['carrierRegionv2'],
        'app_language': 'en',
        'carrier_region': dev_info['geo']['region'],
        'ac2': 'wifi5g',
        'uoo': '0',
        'op_region': dev_info['geo']['region'],
        'timezone_offset': dev_info['geo']['timezoneOffset'],
        'build_number': dev_info['app']['appVersion'],
        'host_abi': dev_info['device']['cpuAbi'],
        'locale': f"{dev_info['geo']['region'].lower()}-{dev_info['geo']['region']}",
        'region': dev_info['geo']['region'],
        'ts': ts // 1000,
        'cdid': dev_info['device']['cdid'],
        'okhttp_version': dev_info['app']['ttnet_version'],
        'use_store_region_cookie': '1'
    }
    return urllib.parse.urlencode(url_params | extra)
