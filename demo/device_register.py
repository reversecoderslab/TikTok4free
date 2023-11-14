import base64
import binascii
import json
import time
import random
from uuid import uuid1

from api import do_get_dev_tmpl, get_device_register_body, do_sign_v5, gen_locals, encrypt_get_token, decrypt_get_token, \
    encrypt_get_seed, decrypt_get_seed, encrypt_get_report
from domains import DOMAIN_APPLOG, DOMAIN_MSSDK, DOMAIN_NORMAL
from request_params import generate_url_common_params, generate_common_header_info
from utils import rand_str, post_request, get_request, to_query_str, printf


class DeviceRegister:
    """
    Device register
    """
    def __init__(self, session, proxy: str = None):
        self.session = session
        self.proxy = proxy
        self.device_id = ""
        self.install_id = ""
        self.dev_info = None

    def process_dev_info(self):
        self.dev_info = do_get_dev_tmpl()

        # Replace other device info

        self.dev_info["openUdid"] = rand_str(40)
        self.dev_info["clientUdid"] = str(uuid1())
        self.dev_info["cdid"] = str(uuid1())
        self.dev_info["androidId"] = rand_str(20)
        self.dev_info["gaId"] = str(uuid1())
        self.dev_info["reqId"] = str(uuid1())
        self.dev_info["IMEI"] = str(random.randint(300000000000000, 394601551608653))
        self.dev_info["mac"] = ':'.join([f'{random.randint(0, 255):02X}' for _ in range(6)])

        dev_locals = gen_locals(self.proxy)["data"]

        printf(f'Locals: {dev_locals}')

        self.dev_info["carrier"] = dev_locals["operator_name"]  # T-Mobile
        self.dev_info["carrierRegion"] = dev_locals["carrier_region"]  # DE
        self.dev_info["carrierRegionv2"] = dev_locals["carrier_region_v2"]  # 262
        self.dev_info["language"] = "en_{}".format(dev_locals["region"])  # DE
        self.dev_info["timezone"] = dev_locals["timezone"]  # 1
        self.dev_info["timezoneName"] = dev_locals["tz_name"]  # Europe/Berlin
        self.dev_info["timezoneOffset"] = int(dev_locals["tz_offset"])  # 3600
        self.dev_info["region"] = dev_locals["region"]  # DE
        self.dev_info["simRegion"] = dev_locals["carrier_region"]  # DE
        self.dev_info["mcc_mnc"] = dev_locals["mcc_mnc"]  # 26211

        self.dev_info[
            "userAgent"] = "com.zhiliaoapp.musically/{} (Linux; U; Android {}; en_{}; {}; Build/{}; Cronet/TTNetVersion:4cac2dc1 2022-07-06 QuicVersion:b67bcffb 2022-01-05)".format(
            self.dev_info["updateVersionCode"], self.dev_info["osVersion"], dev_locals["region"],
            self.dev_info["deviceType"], self.dev_info["roBuildId"])

        self.dev_info["webUa"] = "Dalvik/2.1.0 (Linux; U; Android {}; {} Build/{})".format(self.dev_info["osVersion"],
                                                                                           self.dev_info["deviceType"],
                                                                                           self.dev_info["roBuildId"])

        printf(f'Device info: {self.dev_info}')

        return self.dev_info

    def post_device_register(self):
        """
        Send device register request
        """
        host = DOMAIN_APPLOG
        url = "/service/2/device_register/"
        extra = {
            "uoo": "0",
            "tt_data": "a",
            "ttnet_version": self.dev_info["ttnetVersion"],
            "cronet_version": self.dev_info["cronetVersion"],
            "device_platform": self.dev_info["platform"],
        }

        query_args_str = generate_url_common_params(self.dev_info, extra=extra)
        req_url = f"{DOMAIN_APPLOG}{url}?{query_args_str}"

        body = base64.b64decode(get_device_register_body(self.dev_info)).decode('utf-8')
        printf(f'Device register body hex: {body}')

        timestamp_ms = round(time.time() * 1000)
        timestamp = timestamp_ms // 1000

        x_ladon, x_argus, x_gorgon, x_khronos, x_ss_stub = do_sign_v5(timestamp=timestamp, req_url=req_url,
                                                                      dev_info=self.dev_info, body=bytes.fromhex(body))

        headers = generate_common_header_info(self.dev_info) | {
            "x-tt-dm-status": "login=0;ct=0;rt=7",
            'content-type': 'application/octet-stream;tt-data=a',
            'x-ss-stub': x_ss_stub,
            "x-tt-local-region": self.dev_info["region"],
            'user-agent': self.dev_info["userAgent"],
            'X-Khronos': x_khronos,
            'X-Gorgon': x_gorgon,
            "X-Argus": x_argus,
            "X-Ladon": x_ladon
        }
        response = post_request(self.session, req_url, headers, bytes.fromhex(body))
        obj = json.loads(response.text)
        self.device_id = str(obj["device_id"])
        self.install_id = str(obj["install_id"])
        printf(f"device_id_str: {self.device_id}")
        printf(f"install_id_str: {self.install_id}")

        time.sleep(2)
        return response

    def send_app_alert_check(self):
        """
        Send app alert check
        """
        host = DOMAIN_APPLOG
        url = "/service/2/app_alert_check/"
        extra = {
            "is_upgrade_user": "0",
            "cronet_version": self.dev_info["cronetVersion"],
            "ttnet_version": self.dev_info["ttnetVersion"],
        }

        query_args_str = generate_url_common_params(self.dev_info, extra=extra)
        req_url = f"{host}{url}?{query_args_str}"

        timestamp_ms = round(time.time() * 1000)
        timestamp = timestamp_ms // 1000

        x_ladon, x_argus, x_gorgon, x_khronos, x_ss_stub = do_sign_v5(timestamp=timestamp, req_url=req_url,
                                                                      dev_info=self.dev_info)
        headers = generate_common_header_info(self.dev_info) | {
            "x-tt-dm-status": "login=0;ct=0;rt=7",
            'content-type': 'application/octet-stream;tt-data=a',
            "x-tt-local-region": self.dev_info["region"],
            'user-agent': self.dev_info["userAgent"],
            'X-Khronos': x_khronos,
            'X-Gorgon': x_gorgon,
            "X-Argus": x_argus,
            "X-Ladon": x_ladon
        }

        response = get_request(self.session, req_url, headers)
        obj = json.loads(response.text)
        printf(str(obj))

        time.sleep(2)

    def send_device_trust_users(self):
        """
        Send device trust users
        """
        host = DOMAIN_NORMAL
        url = "/passport/device/trust_users/"
        extra = {
            "support_webview": "1",
            "cronet_version": self.dev_info["cronetVersion"],
            "ttnet_version": self.dev_info["ttnetVersion"],
            "use_store_region_cookie": "1"
        }

        query_args_str = generate_url_common_params(self.dev_info, extra=extra)
        req_url = f"{host}{url}?{query_args_str}"

        timestamp_ms = round(time.time() * 1000)
        timestamp = timestamp_ms // 1000

        x_ladon, x_argus, x_gorgon, x_khronos, x_ss_stub = do_sign_v5(timestamp=timestamp, req_url=req_url,
                                                                      dev_info=self.dev_info)
        headers = generate_common_header_info(self.dev_info) | {
            "x-tt-dm-status": "login=0;ct=0;rt=7",
            'content-type': 'application/octet-stream;tt-data=a',
            "x-tt-local-region": self.dev_info["region"],
            'user-agent': self.dev_info["userAgent"],
            'X-Khronos': x_khronos,
            'X-Gorgon': x_gorgon,
            "X-Argus": x_argus,
            "X-Ladon": x_ladon
        }

        body = 'last_sec_user_id=&d_ticket=&last_login_way=-1&last_login_time=0&last_login_platform='
        response = post_request(self.session, req_url, headers, body)
        obj = json.loads(response.text)
        printf(str(obj))

    def send_teen_mode(self):
        """
        Send teen mode
        """
        host = DOMAIN_NORMAL
        url = "/aweme/v1/compliance/settings/"
        extra = {
            "teen_mode_status": "0",
            "ftc_child_mode": "-1"
        }

        query_args_str = generate_url_common_params(self.dev_info, extra=extra)
        req_url = f"{host}{url}?{query_args_str}"

        timestamp_ms = round(time.time() * 1000)
        timestamp = timestamp_ms // 1000

        x_ladon, x_argus, x_gorgon, x_khronos, x_ss_stub = do_sign_v5(timestamp=timestamp, req_url=req_url,
                                                                      dev_info=self.dev_info)
        headers = generate_common_header_info(self.dev_info) | {
            "x-tt-dm-status": "login=0;ct=0;rt=7",
            'content-type': 'application/octet-stream;tt-data=a',
            "x-tt-local-region": self.dev_info["region"],
            'user-agent': self.dev_info["userAgent"],
            'X-Khronos': x_khronos,
            'X-Gorgon': x_gorgon,
            "X-Argus": x_argus,
            "X-Ladon": x_ladon
        }

        response = get_request(self.session, req_url, headers)
        obj = json.loads(response.text)
        printf(str(obj))

        time.sleep(2)

        return obj['cmpl_enc']

    def send_compliance_settings(self):
        """
        Send compliance settings
        """
        host = DOMAIN_NORMAL
        url = "/tiktok/v1/ultimate/cmpl/settings/"

        query_args_str = generate_url_common_params(self.dev_info)
        req_url = f"{host}{url}?{query_args_str}"

        timestamp_ms = round(time.time() * 1000)
        timestamp = timestamp_ms // 1000

        x_ladon, x_argus, x_gorgon, x_khronos, x_ss_stub = do_sign_v5(timestamp=timestamp, req_url=req_url,
                                                                      dev_info=self.dev_info)
        headers = generate_common_header_info(self.dev_info) | {
            "x-tt-dm-status": "login=0;ct=0;rt=7",
            'content-type': 'application/octet-stream;tt-data=a',
            "x-tt-local-region": self.dev_info["region"],
            'user-agent': self.dev_info["userAgent"],
            'X-Khronos': x_khronos,
            'X-Gorgon': x_gorgon,
            "X-Argus": x_argus,
            "X-Ladon": x_ladon
        }

        response = get_request(self.session, req_url, headers)
        obj = json.loads(response.text)
        printf(str(obj))

        time.sleep(3)

    def get_token(self):
        """
        MSSDK send get_token get sec_did_token
        """
        timestamp_ms = round(time.time() * 1000)
        timestamp = timestamp_ms // 1000

        host = DOMAIN_MSSDK
        url = "/sdi/get_token"

        query_args = {
            "aid": self.dev_info["appId"],
            "iid": self.install_id,
            "did": self.device_id,
            "client_type": "inhouse",
            "mode": "2",
            "lc_id": self.dev_info["licenseId"],
            "app_ver": self.dev_info["appVersion"],
            "sdk_ver": self.dev_info["MSSDKVersion"],
            "platform": self.dev_info["platform"],
            "region_type": self.dev_info["regionType"],
            "sdk_ver_code": self.dev_info["MSSDKVersionCode"],
            "version_code": self.dev_info["updateVersionCode"],
            "device_platform": self.dev_info["platform"],
        }
        query_args_str = to_query_str(query_args)
        req_url = f"{host}{url}?{query_args_str}{'&skid&subaid&bd_did'}"
        body = encrypt_get_token(self.dev_info)
        x_ladon, x_argus, x_gorgon, x_khronos, x_ss_stub = do_sign_v5(dev_info=self.dev_info,
                                                                      timestamp=timestamp,
                                                                      req_url=req_url,
                                                                      body=body)
        header = generate_common_header_info(self.dev_info) | {
            "x-tt-dm-status": "login=0;ct=0;rt=7",
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": self.dev_info["userAgent"],
            "x-ss-stub": x_ss_stub,
            'X-Khronos': x_khronos,
            'X-Gorgon': x_gorgon,
            "X-Argus": x_argus,
            "X-Ladon": x_ladon
        }
        resp = post_request(self.session, req_url, header, post_body=body)
        ret = decrypt_get_token(self.dev_info["os"].lower(), self.dev_info["appId"], resp.content)
        printf(ret)
        try:
            time.sleep(2)
            return ret["token"]
        except:
            raise ('No token')

    def get_seed(self):
        """
        MSSDK send get_seed get seed
        """
        timestamp_ms = round(time.time() * 1000)
        timestamp = timestamp_ms // 1000

        host = DOMAIN_MSSDK
        url = "/ms/get_seed"

        query_args = {
            "aid": self.dev_info["appId"],
            "iid": self.install_id,
            "did": self.device_id,
            "client_type": "inhouse",
            "mode": "2",
            "lc_id": self.dev_info["licenseId"],
            "app_ver": self.dev_info["appVersion"],
            "sdk_ver": self.dev_info["MSSDKVersion"],
            "platform": self.dev_info["platform"],
            "region_type": self.dev_info["regionType"],
            "sdk_ver_code": self.dev_info["MSSDKVersionCode"],
            "version_code": self.dev_info["updateVersionCode"],
            "device_platform": self.dev_info["platform"],
        }
        query_args_str = to_query_str(query_args)
        req_url = f"{host}{url}?{query_args_str}{'&sdkid&subaid&bd_did'}"
        body = encrypt_get_seed(self.dev_info)
        x_ladon, x_argus, x_gorgon, x_khronos, x_ss_stub = do_sign_v5(dev_info=self.dev_info,
                                                                      timestamp=timestamp,
                                                                      req_url=req_url,
                                                                      body=body)
        header = generate_common_header_info(self.dev_info) | {
            "x-tt-dm-status": "login=0;ct=0;rt=7",
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": self.dev_info["userAgent"],
            "x-ss-stub": x_ss_stub,
            'X-Khronos': x_khronos,
            'X-Gorgon': x_gorgon,
            "X-Argus": x_argus,
            "X-Ladon": x_ladon
        }
        resp = post_request(self.session, req_url, header, post_body=body)
        printf(binascii.hexlify(resp.content).decode('utf-8'))
        ret = decrypt_get_seed(self.dev_info["os"].lower(), self.dev_info["appId"],
                               binascii.hexlify(resp.content).decode('utf-8'))
        printf(ret)
        time.sleep(1)
        return ret

    def post_ri_report(self, account_info=None):
        """
        MSSDK send risk report
        """
        timestamp_ms = round(time.time() * 1000)
        timestamp = timestamp_ms // 1000

        host = DOMAIN_MSSDK
        url = "/ri/report"

        query_args = {
            "aid": self.dev_info["appId"],
            "iid": self.install_id,
            "did": self.device_id,
            "mode": "2",
            "lc_id": self.dev_info["licenseId"],
            "app_ver": self.dev_info["appVersion"],
            "sdk_ver": self.dev_info["MSSDKVersion"],
            "platform": self.dev_info["platform"],
            "region_type": self.dev_info["regionType"],
            "sdk_ver_code": self.dev_info["MSSDKVersionCode"],
            "version_code": self.dev_info["appVersionCode"],
            "device_platform": self.dev_info["platform"],
        }
        query_args_str = to_query_str(query_args)
        req_url = f"{host}{url}?{query_args_str}{'&skid&subaid&bd_did'}"

        body = encrypt_get_report(self.dev_info)
        x_ladon, x_argus, x_gorgon, x_khronos, x_ss_stub = do_sign_v5(dev_info=self.dev_info,
                                                                      timestamp=timestamp,
                                                                      req_url=req_url,
                                                                      body=body)
        header = generate_common_header_info(self.dev_info) | {
            "x-tt-dm-status": "login=0;ct=1;rt=6",
            "content-type": "application/octet-stream",
            "user-agent": "ByteDance-MSSDK",
            "x-ss-stub": x_ss_stub,
            'X-Khronos': x_khronos,
            'X-Gorgon': x_gorgon,
            "X-Argus": x_argus,
            "X-Ladon": x_ladon
        }
        if account_info is not None:
            header |= {
                'x-tt-token': account_info["x-tt-token"],
                'x-tt-cmpl-token': account_info["cookies"]["cmpl_token"],
            }
            resp = post_request(self.session, req_url, header, post_body=body, cookies=account_info["cookies"])
        else:
            resp = post_request(self.session, req_url, header, post_body=body)
        printf(resp)

        time.sleep(2)
