from request_params import *
from api import *


def tt_common_post_request(session, dev_info, account_info, host, url, body=None, extra=None):
    """

    :param session:
    :param dev_info:
    :param account_info:
    :param host:
    :param url:
    :param body:
    :return:
    """
    url_params = generate_url_common_params(dev_info, extra if extra else None)
    query_str = f"{host}{url}?{url_params}"

    timestamp_ms = round(time.time() * 1000)
    x_ladon, x_argus, x_gorgon, x_khronos, x_ss_stub = do_sign_v5(dev_info, int(timestamp_ms / 1000), query_str, body=body)
    headers = {
        "accept-encoding": "gzip",
        "x-tt-app-init-region": f"carrierregion={dev_info['geo']['region']};mccmnc={dev_info['geo']['mcc_mnc']};sysregion={dev_info['geo']['region']};appregion={dev_info['geo']['region']}",
        "log-encode-type": "gzip",
        "x-tt-dm-status": "login=0;ct=0;rt=7",
        "passport-sdk-settings": "x-tt-token,sec_user_id",
        "passport-sdk-sign": "x-tt-token,sec_user_id",
        "x-tt-request-tag": "t=0;n=1",
        "x-ss-req-ticket": str(round(time.time() * 1000)),
        "sdk-version": "2",
        "passport-sdk-version": "6010290",
        "x-vc-bdturing-sdk-version": "2.3.7.i18n",
        "user-agent": dev_info['extra']['userAgent'],
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "host": dev_info['geo']['domain_normal'].split('//')[1],
        "connection": "Keep-Alive",
        "cookie": cookie_string(dev_info['extra']['cookies']),
        "x-tt-trace-id": get_trace_id(dev_info['app']['appId'], dev_info['device']['deviceId']),
        'x-ss-stub': x_ss_stub,
        'X-Khronos': x_khronos,
        'X-Gorgon': x_gorgon,
        "X-Argus": x_argus,
        "X-Ladon": x_ladon
    }

    print(query_str)
    if account_info is not None:
        headers |= {
            'x-tt-token': account_info["x-tt-token"],
            'x-tt-cmpl-token': account_info["cookies"]["cmpl_token"],
            'x-bd-client-key': account_info["x-bd-client-key"],
            'x-bd-kmsv': account_info["x-bd-kmsv"],
        }
        response = post_request(session, query_str, headers, post_body=body, cookies=account_info["cookies"])
    else:
        headers |= {
            "x-tt-dm-status": "login=0;ct=1;rt=6",
        }
        response = post_request(session, query_str, headers, post_body=body)
    print(response.content)
    return response


def tt_common_get_request(session, dev_info, account_info, host, url, extra={}):
    """

    :param session:
    :param dev_info:
    :param account_info:
    :param host:
    :param url:
    :param extra:
    :return:
    """
    url_params = generate_url_common_params(dev_info, extra)
    query_str = f"{host}{url}?{url_params}"

    timestamp_ms = round(time.time() * 1000)
    x_ladon, x_argus, x_gorgon, x_khronos, x_ss_stub = do_sign_v5(dev_info, int(timestamp_ms / 1000), query_str)
    headers = {
        "accept-encoding": "gzip",
        "x-tt-app-init-region": f"carrierregion={dev_info['geo']['region']};mccmnc={dev_info['geo']['mcc_mnc']};sysregion={dev_info['geo']['region']};appregion={dev_info['geo']['region']}",
        "log-encode-type": "gzip",
        "x-tt-dm-status": "login=0;ct=0;rt=7",
        "passport-sdk-settings": "x-tt-token,sec_user_id",
        "passport-sdk-sign": "x-tt-token,sec_user_id",
        "x-tt-request-tag": "t=0;n=1",
        "x-ss-req-ticket": str(round(time.time() * 1000)),
        "sdk-version": "2",
        "passport-sdk-version": "6010290",
        "x-vc-bdturing-sdk-version": "2.3.7.i18n",
        "user-agent": dev_info['extra']['userAgent'],
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "host": dev_info['geo']['domain_normal'].split('//')[1],
        "connection": "Keep-Alive",
        "cookie": cookie_string(dev_info['extra']['cookies']),
        "x-tt-trace-id": get_trace_id(dev_info['app']['appId'], dev_info['device']['deviceId']),
        'X-Khronos': x_khronos,
        'X-Gorgon': x_gorgon,
        "X-Argus": x_argus,
        "X-Ladon": x_ladon
    }

    print(query_str)
    if account_info is not None:
        headers |= {
            'x-tt-token': account_info["x-tt-token"],
            'x-tt-cmpl-token': account_info["cookies"]["cmpl_token"],
            'x-bd-client-key': account_info["x-bd-client-key"],
            'x-bd-kmsv': account_info["x-bd-kmsv"],
        }
        response = get_request(session, query_str, headers, cookies=account_info["cookies"])
    else:
        headers |= {
            "x-tt-dm-status": "login=0;ct=1;rt=6",
        }
        response = get_request(session, query_str, headers)
    print(response.content)
    return response
