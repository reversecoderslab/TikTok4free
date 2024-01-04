# Support: (Discord server: https://discord.gg/qDDSzY9TPP)

import random
from random import choices

import requests
from device_register import DeviceRegister
from domains import DOMAIN_CORE
from request_tiktok import tt_common_get_request
from utils import printf, cookie_to_str
import time


def get_other_user_profile(session, dev_info, account_info, to_user_id, to_sec_user_id):
    """

    :param session:
    :param dev_info:
    :param account_info:
    :param to_user_id:
    :param to_sec_user_id:
    :return:
    """
    extra = {
        'user_id': to_user_id,
        'address_book_access': '1',
        'sec_user_id': to_sec_user_id,
        'user_avatar_shrink': '188_188',
    }
    return tt_common_get_request(session, dev_info, account_info, DOMAIN_CORE, "/aweme/v1/user/profile/other/", extra)


if __name__ == "__main__":
    # -------- START ONLY CHANGE HERE -------- #
    proxy = None
    #token = ''.join(choices('0123456789abcdefghiklmnopqrstuvwxyz', k=8))
    #proxy = f'xxx:xxx_country-{random.choice(["de", "cz", "es", "it"])}_session-{token}_lifetime-5m@geo.iproyal.com:12321'

    get_user_profile = None
    # -------- END ONLY CHANGE HERE -------- #

    session = requests.Session()
    if proxy:
        session.proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}

    device = DeviceRegister(proxy=proxy, session=session)

    timestamp_ms = round(time.time() * 1000)
    timestamp = timestamp_ms // 1000
    dev_info['launchFirstTime'] = str(timestamp)

    printf(f'\n==== START GET DEVICE TEMPLATE ====')
    device.process_dev_info()
    printf(f'\n==== END GET DEVICE TEMPLATE ====')

    printf(f'\n==== START REGISTER DEVICE ====')
    r = device.post_device_register()
    dev_info = device.dev_info
    dev_info["installId"] = device.install_id
    dev_info["deviceId"] = device.device_id
    if dev_info["installId"] and dev_info["deviceId"] == 0 or dev_info["installId"] and dev_info["deviceId"] == '' or \
            dev_info["installId"] and dev_info["deviceId"] == '0':
        printf('Device not registered')
        raise ('Device not registered')
    dev_info['cookies'] = cookie_to_str(r.cookies.get_dict(), None)
    printf(f'\n==== END REGISTER DEVICE ====')

    printf("\n==== START GET SEED ====")
    obj = device.get_seed()
    try:
        dev_info["seed"] = obj['data']['seed']
        dev_info["seedAlgorithm"] = obj['algorithm']
    except:
        printf('No seed')
        raise ('No seed')
    printf("\n==== END GET SEED ====")

    printf(f'\n==== START APP ALERT CHECK ====')
    device.send_app_alert_check()
    printf(f'\n==== END APP ALERT CHECK ====')

    printf(f'\n==== START GET SEC DEV ID ====')
    token = device.get_token()
    printf(f'\n==== END GET SEC DEV ID ====')

    printf(f"\n==== START RI REPORT ====")
    dev_info["secDeviceIdToken"] = token
    device.post_ri_report()
    printf("\n==== END ri/report ====")

    printf("\n==== START DEVICE INFO ====")
    printf(dev_info)
    printf("\n==== END DEVICE INFO ====")

    if get_user_profile:
        # get_other_user_profile
        account_info = {
            "cookies": {
                "ttreq": "",
                "sid_tt": "",
                "uid_tt": "",
                "odin_tt": "",
                "sessionid": "",
                "sid_guard": "",
                "msToken": "",
                "store-idc": "",
                "uid_tt_ss": "",
                "cmpl_token": "",
                "install_id": "",
                "multi_sids": "",
                "sessionid_ss": "",
                "tt-target-idc": "",
                "store-country-code": "",
                "passport_csrf_token": "",
                "passport_csrf_token_default": ""
            },
            "x-tt-token": "",

        }
        res = get_other_user_profile(session, dev_info, account_info, "to_user_id", "to_sec_user_id")
        print(f'\n{res.text}')
