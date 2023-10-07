from request_params import *
from api import *


def tt_common_post_request(session, dev_info, account_info, host, url, body=None):
    """

    :param session:
    :param dev_info:
    :param account_info:
    :param host:
    :param url:
    :param body:
    :return:
    """
    url_params = generate_url_common_params(dev_info)
    query_str = f"{host}{url}?{url_params}"

    timestamp_ms = round(time.time() * 1000)
    x_ladon, x_argus, x_gorgon, x_khronos, x_ss_stub = do_sign_v5(dev_info, int(timestamp_ms / 1000), query_str, body=body)
    headers = generate_common_header_info(dev_info)
    headers |= {
        'content-type': 'application/json',
        'x-ss-stub': x_ss_stub,
        'X-Khronos': x_khronos,
        'X-Gorgon': x_gorgon,
        "X-Argus": x_argus,
        "X-Ladon": x_ladon
    }

    if account_info is not None:
        headers |= {
            'x-tt-token': account_info["x-tt-token"],
            'x-tt-cmpl-token': account_info["cookies"]["cmpl_token"],
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
    headers = generate_common_header_info(dev_info)
    headers |= {
        'content-type': 'application/x-www-form-urlencoded',
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
        }
        response = get_request(session, query_str, headers, cookies=account_info["cookies"])
    else:
        headers |= {
            "x-tt-dm-status": "login=0;ct=1;rt=6",
        }
        response = get_request(session, query_str, headers)
    print(response.content)
    return response