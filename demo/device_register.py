import base64
import binascii
import json
import time

from api            import do_get_dev_tmpl, get_device_register_body, do_sign_v5, encrypt_get_token, decrypt_get_token, encrypt_get_seed, decrypt_get_seed, encrypt_get_report, encrypt_get_setting
from domains        import DOMAIN_APPLOG, DOMAIN_MSSDK, DOMAIN_NORMAL
from request_params import generate_url_common_params
from utils          import post_request, get_request, to_query_str, printf, cookie_string, cookie_json, get_trace_id


class DeviceRegister:
    """
    Device register
    """

    def __init__(self, session, country, proxy: str = None):
        self.session    = session
        self.proxy      = proxy
        self.device_id  = ""
        self.install_id = ""
        self.dev_info   = None
        self.country    = country

    def process_dev_info(self):
        self.dev_info = do_get_dev_tmpl(self.proxy, self.country)
        printf(f'Device info: {self.dev_info}')

        return self.dev_info

    def post_device_register(self):
        """
        Send device register request
        """
        host = DOMAIN_APPLOG
        url = "/service/2/device_register/"
        ts = round(time.time() * 1000)
        extra = {
            'tt_data': 'a',
            'last_install_time': ts // 1000,
        }

        query_args_str = generate_url_common_params(self.dev_info, extra=extra)
        req_url = f"{DOMAIN_APPLOG}{url}?{query_args_str}"

        body = base64.b64decode(get_device_register_body(self.dev_info)).decode('utf-8')
        printf(f'Device register body hex: {body}')

        timestamp_ms = round(time.time() * 1000)
        timestamp = timestamp_ms // 1000

        x_ladon, x_argus, x_gorgon, x_khronos, x_ss_stub = do_sign_v5(timestamp=timestamp, req_url=req_url,
                                                                      dev_info=self.dev_info, body=bytes.fromhex(body))

        headers = {
            "accept-encoding": "gzip",
            "x-tt-app-init-region": f"carrierregion={self.dev_info['geo']['region']};mccmnc={self.dev_info['geo']['mcc_mnc']};sysregion={self.dev_info['geo']['region']};appregion={self.dev_info['geo']['region']}",
            "log-encode-type": "gzip",
            "x-tt-request-tag": "t=0;n=1",
            "x-ss-req-ticket": str(round(time.time() * 1000)),
            "pns_event_id": "16",
            "sdk-version": "2",
            "passport-sdk-version": "6010290",
            "x-vc-bdturing-sdk-version": "2.3.7.i18n",
            "user-agent": self.dev_info['extra']['userAgent'],
            "content-type": "application/octet-stream;tt-data=a",
            "host": self.dev_info['geo']['domain_applog'].split('//')[1],
            "connection": "Keep-Alive",
            "cookie": "store-idc=; tt-target-idc=; store-country-code=",
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
        if not response.cookies:
            pass
        else:
            cookies_dict = cookie_json(response)
            self.dev_info['extra']['cookies'] = json.loads(json.dumps(cookies_dict, indent=4))

        return response

    def send_app_alert_check(self):
        """
        Send app alert check
        """
        host = DOMAIN_APPLOG
        url = "/service/2/app_alert_check/"
        extra = {
            'device_id': self.dev_info['device']['deviceId'],
            'iid': self.dev_info['device']['installId'],
            "tt_info": "dGMFEAAAbLoElhswdJ8gjebFKpZYPGYD_PkJZrX6Ur7-Z_UGkWEVjGvOkezaKZ1l_tc1cJiNexcu%0AePB-JGWgvJyZt7Np7dGWAUlsvmw8nAre3LDJ7P6KOcrmLvJVHgatVkNDwvnlC2xz-BnuqjLIgj4f%0A1ONKs4SJFa6PdwHXvVAiHOIo0Hg2d8pDZhd6u7YoEAHPrbth-h2d3qZWnwkwUglA7CjBFAoKTpIH%0ATUuoMidzlVPFR1VIRGA-Q0gDuVIocj8u4C-ltQ9iqjGoqZGaRIduCT2x2gUfuwzM3Xy9Fai57E8B%0AvC5n35IbhHAgVG4n0FWR4_OQvdXieeNwzZcmBvFD2zDxufltGonhZeD39fPc4uwb66x8k-oq0vCK%0Ab_BO2OlklGmeejBeTWMt7uW6HMQAnTgNwBZGwV5FFLkh5dYJEBjlYzIdyaobSpYDny_siL3gC4p7%0Ah90Ee2wb5bu3lyW3FomDL1ekQySczvDY7Jaxjd9gUMO9HPXH6foLhHvFDf7gb9fyEv_OoStCpC03%0ATrbtDfGAQ8W_fqk2ZNl1hUO12kqqBPa_InwMwIRPhxnD0BkyebPkde_BYFjz59oKn1ukipGT53I4%0A-9rjDBWvdZ-D2Mc3zcrXCv4pVb7gUI_f6y1oUJ3psjf6feIDSgx2OFsTAVrp2R38ux4xPM6ZNNb2%0AZK1Z1gFpjATL4cDHe1J8vivTuVh-gwWrT69kIfjZJVwjjV-4XwdljHoiFrZvjSovSci3Xyfzpyld%0AoOuzhaZJsK9usTEZALnQu2uFG0eBmL3toXhbuoUKKJHKU1E3lZ8WADvhvCzl6rqhV4XFt-aYjK9D%0A_i5JNLdw5ceigousCm53paXIiA%3D%3D%0A"
        }

        query_args_str = generate_url_common_params(self.dev_info, extra=extra)
        req_url = f"{host}{url}?{query_args_str}"

        timestamp_ms = round(time.time() * 1000)
        timestamp = timestamp_ms // 1000

        x_ladon, x_argus, x_gorgon, x_khronos, x_ss_stub = do_sign_v5(timestamp=timestamp, req_url=req_url,
                                                                      dev_info=self.dev_info)
        headers = {
            "accept-encoding": "gzip",
            "x-tt-app-init-region": f"carrierregion={self.dev_info['geo']['region']};mccmnc={self.dev_info['geo']['mcc_mnc']};sysregion={self.dev_info['geo']['region']};appregion={self.dev_info['geo']['region']}",
            "x-ss-req-ticket": str(round(time.time() * 1000)),
            "pns_event_id": "10",
            "sdk-version": "2",
            "passport-sdk-version": "6010290",
            "x-vc-bdturing-sdk-version": "2.3.7.i18n",
            "user-agent": self.dev_info['extra']['userAgent'],
            "host": self.dev_info['geo']['domain_applog'].split('//')[1],
            "connection": "Keep-Alive",
            "cookie": cookie_string(self.dev_info['extra']['cookies']),
            'X-Khronos': x_khronos,
            'X-Gorgon': x_gorgon,
            "X-Argus": x_argus,
            "X-Ladon": x_ladon
        }

        response = get_request(self.session, req_url, headers)
        obj = json.loads(response.text)
        if not response.cookies:
            pass
        else:
            cookies_dict = cookie_json(response)
            self.dev_info['extra']['cookies'] = json.loads(json.dumps(cookies_dict, indent=4))
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
        }

        query_args_str = generate_url_common_params(self.dev_info, extra=extra)
        req_url = f"{host}{url}?{query_args_str}"

        timestamp_ms = round(time.time() * 1000)
        timestamp = timestamp_ms // 1000

        body = "last_sec_user_id=&d_ticket=&last_login_way=-1&last_login_time=0&last_login_platform="

        x_ladon, x_argus, x_gorgon, x_khronos, x_ss_stub = do_sign_v5(timestamp=timestamp, req_url=req_url,
                                                                      dev_info=self.dev_info, body=body)
        headers = {
            "accept-encoding": "gzip",
            "x-tt-app-init-region": f"carrierregion={self.dev_info['geo']['region']};mccmnc={self.dev_info['geo']['mcc_mnc']};sysregion={self.dev_info['geo']['region']};appregion={self.dev_info['geo']['region']}",
            "log-encode-type": "gzip",
            "x-tt-dm-status": "login=0;ct=0;rt=7",
            "x-tt-request-tag": "t=0;n=1",
            "x-ss-req-ticket": str(round(time.time() * 1000)),
            "sdk-version": "2",
            "passport-sdk-version": "6010290",
            "x-vc-bdturing-sdk-version": "2.3.7.i18n",
            "user-agent": self.dev_info['extra']['userAgent'],
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "host": self.dev_info['geo']['domain_normal'].split('//')[1],
            "connection": "Keep-Alive",
            "cookie": cookie_string(self.dev_info['extra']['cookies']),
            "x-tt-trace-id": get_trace_id(self.dev_info['app']['appId'], self.dev_info['device']['deviceId']),
            "x-ss-stub": x_ss_stub,
            'X-Khronos': x_khronos,
            'X-Gorgon': x_gorgon,
            "X-Argus": x_argus,
            "X-Ladon": x_ladon
        }

        response = post_request(self.session, req_url, headers, body)
        if not response.cookies:
            pass
        else:
            cookies_dict = cookie_json(response)
            self.dev_info['extra']['cookies'].update(json.loads(json.dumps(cookies_dict, indent=4)))
        obj = json.loads(response.text)
        printf(str(obj))

    def get_token(self):
        """
        MSSDK send get_token get sec_did_token
        """
        timestamp_ms = round(time.time() * 1000)
        timestamp = timestamp_ms // 1000

        host = DOMAIN_MSSDK
        url = "/sdi/get_token"

        query_args = {
            "lc_id": self.dev_info['extra']['licenseId'],
            "platform": "android",
            "device_platform": "android",
            "sdk_ver": self.dev_info['extra']['MSSDKVersion'],
            "sdk_ver_code": self.dev_info['extra']['MSSDKVersionCode'],
            "app_ver": self.dev_info['app']['appVersion'],
            "version_code": self.dev_info['app']['updateVersionCode'],
            "aid": self.dev_info['app']['appId'],
            "sdkid": "",
            "subaid": "",
            "iid": self.dev_info['device']['installId'],
            "did": self.dev_info['device']['deviceId'],
            "bd_did": "",
            "client_type": "inhouse",
            "region_type": "ov",
            "mode": "2"
        }
        query_args_str = to_query_str(query_args)
        req_url = f"{host}{url}?{query_args_str}"
        body = encrypt_get_token(self.dev_info)
        x_ladon, x_argus, x_gorgon, x_khronos, x_ss_stub = do_sign_v5(dev_info=self.dev_info,
                                                                      timestamp=timestamp,
                                                                      req_url=req_url,
                                                                      body=body)
        header = {
            "accept-encoding": "gzip",
            "accept": "*/*",
            "x-vc-bdturing-sdk-version": "2.3.7.i18n",
            "sdk-version": "2",
            "x-ss-req-ticket": str(round(time.time() * 1000)),
            "X-Tt-Dm-Status": "login=0;ct=0;rt=7",
            "passport-sdk-version": "6010290",
            "x-tt-store-region": self.dev_info['geo']['region'].lower(),
            "x-tt-store-region-src": self.dev_info['extra']['cookies']['store-country-code-src'],
            "user-agent": self.dev_info['extra']['userAgent'],
            "content-type": "application/octet-stream",
            "host": DOMAIN_MSSDK.split('/')[2],
            "connection": "Keep-Alive",
            "cookie": cookie_string(self.dev_info['extra']['cookies']),
            'x-ss-dp': '1233',
            'x-tt-dm-status': 'login=0;ct=1;rt=6',
            'x-tt-request-tag': 't=0;n=1;s=0',
            "x-ss-stub": x_ss_stub,
            'X-Khronos': x_khronos,
            'X-Gorgon': x_gorgon,
            "X-Argus": x_argus,
            "X-Ladon": x_ladon
        }
        resp = post_request(self.session, req_url, header, post_body=body)
        ret = decrypt_get_token(self.dev_info["device"]["os"].lower(), self.dev_info["app"]["appId"],
                                binascii.hexlify(resp.content).decode('utf-8'))
        if not resp.cookies:
            pass
        else:
            cookies_dict = cookie_json(resp)
            self.dev_info['extra']['cookies'] = json.loads(json.dumps(cookies_dict, indent=4))
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
            "lc_id": self.dev_info['extra']['licenseId'],
            "platform": "android",
            "device_platform": "android",
            "sdk_ver": self.dev_info['extra']['MSSDKVersion'],
            "sdk_ver_code": self.dev_info['extra']['MSSDKVersionCode'],
            "app_ver": self.dev_info['app']['appVersion'],
            "version_code": self.dev_info['app']['updateVersionCode'],
            "aid": self.dev_info['app']['appId'],
            "sdkid": "",
            "subaid": "",
            "iid": self.dev_info['device']['installId'],
            "did": self.dev_info['device']['deviceId'],
            "bd_did": "",
            "client_type": "inhouse",
            "region_type": "ov",
            "mode": "2"
        }
        query_args_str = to_query_str(query_args)
        req_url = f"{host}{url}?{query_args_str}"
        body = encrypt_get_seed(self.dev_info)
        x_ladon, x_argus, x_gorgon, x_khronos, x_ss_stub = do_sign_v5(dev_info=self.dev_info,
                                                                      timestamp=timestamp,
                                                                      req_url=req_url,
                                                                      body=body)

        header = {
            "accept-encoding": "gzip",
            "accept": "*/*",
            "x-vc-bdturing-sdk-version": "2.3.7.i18n",
            "sdk-version": "2",
            "x-ss-req-ticket": str(round(time.time() * 1000)),
            "X-Tt-Dm-Status": "login=0;ct=0;rt=7",
            "passport-sdk-version": "6010290",
            "x-tt-store-region": self.dev_info['geo']['region'].lower(),
            "x-tt-store-region-src": self.dev_info['extra']['cookies']['store-country-code-src'],
            "user-agent": self.dev_info['extra']['userAgent'],
            "content-type": "application/octet-stream",
            "host": DOMAIN_MSSDK.split('/')[2],
            "connection": "Keep-Alive",
            "cookie": cookie_string(self.dev_info['extra']['cookies']),
            'x-ss-dp': '1233',
            'x-tt-dm-status': 'login=0;ct=1;rt=6',
            'x-tt-request-tag': 't=0;n=1;s=0',
            "x-ss-stub": x_ss_stub,
            'X-Khronos': x_khronos,
            'X-Gorgon': x_gorgon,
            "X-Argus": x_argus,
            "X-Ladon": x_ladon
        }
        resp = post_request(self.session, req_url, header, post_body=body)
        printf(binascii.hexlify(resp.content).decode('utf-8'))
        ret = decrypt_get_seed(self.dev_info["device"]["os"].lower(), self.dev_info["app"]["appId"],
                               binascii.hexlify(resp.content).decode('utf-8'))
        if not resp.cookies:
            pass
        else:
            cookies_dict = cookie_json(resp)
            self.dev_info['extra']['cookies'] = json.loads(json.dumps(cookies_dict, indent=4))
        printf(ret)
        time.sleep(1)
        return ret

    def post_ri_report(self, mode, account_info=None):
        """
        MSSDK send risk report
        """
        timestamp_ms = round(time.time() * 1000)
        timestamp = timestamp_ms // 1000

        host = DOMAIN_MSSDK
        url = "/ri/report"

        query_args = {
            "lc_id": self.dev_info['extra']['licenseId'],
            "platform": "android",
            "device_platform": "android",
            "sdk_ver": self.dev_info['extra']['MSSDKVersion'],
            "sdk_ver_code": self.dev_info['extra']['MSSDKVersionCode'],
            "app_ver": self.dev_info['app']['appVersion'],
            "version_code": self.dev_info['app']['updateVersionCode'],
            "aid": self.dev_info['app']['appId'],
            "sdkid": "",
            "subaid": "",
            "iid": self.dev_info['device']['installId'],
            "did": self.dev_info['device']['deviceId'],
            "bd_did": "",
            "client_type": "inhouse",
            "region_type": "ov",
            "mode": "2"
        }
        query_args_str = to_query_str(query_args)
        req_url = f"{host}{url}?{query_args_str}"

        body = encrypt_get_report(self.dev_info, mode)
        x_ladon, x_argus, x_gorgon, x_khronos, x_ss_stub = do_sign_v5(dev_info=self.dev_info,
                                                                      timestamp=timestamp,
                                                                      req_url=req_url,
                                                                      body=body)
        header = {
            "accept-encoding": "gzip",
            "accept": "*/*",
            "x-vc-bdturing-sdk-version": "2.3.7.i18n",
            "sdk-version": "2",
            "x-ss-req-ticket": str(round(time.time() * 1000)),
            "passport-sdk-version": "6010290",
            "x-tt-store-region": self.dev_info['geo']['region'].lower(),
            "x-tt-store-region-src": self.dev_info['extra']['cookies']['store-country-code-src'],
            "user-agent": self.dev_info['extra']['userAgent'],
            "content-type": "application/octet-stream",
            "host": DOMAIN_MSSDK.split('/')[2],
            "connection": "Keep-Alive",
            "cookie": cookie_string(self.dev_info['extra']['cookies']),
            'x-ss-dp': '1233',
            'x-tt-dm-status': 'login=0;ct=1;rt=6',
            'x-tt-request-tag': 't=0;n=1;s=0',
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
        if not resp.cookies:
            pass
        else:
            cookies_dict = cookie_json(resp)
            self.dev_info['extra']['cookies'] = json.loads(json.dumps(cookies_dict, indent=4))
        printf(resp)

        time.sleep(2)

    def post_mscc_setting(self, account_info=None):
        """
        MSSDK send mscc setting
        """
        timestamp_ms = round(time.time() * 1000)
        timestamp = timestamp_ms // 1000

        host = DOMAIN_MSSDK
        url = "/mscc/common_setting"

        query_args = {
            "lc_id": self.dev_info['extra']['licenseId'],
            "platform": "android",
            "device_platform": "android",
            "sdk_ver": self.dev_info['extra']['MSSDKVersion'],
            "sdk_ver_code": self.dev_info['extra']['MSSDKVersionCode'],
            "app_ver": self.dev_info['app']['appVersion'],
            "version_code": self.dev_info['app']['updateVersionCode'],
            "aid": self.dev_info['app']['appId'],
            "sdkid": "",
            "subaid": "",
            "iid": self.dev_info['device']['installId'],
            "did": self.dev_info['device']['deviceId'],
            "bd_did": "",
            "client_type": "inhouse",
            "region_type": "ov",
            "mode": "2"
        }
        query_args_str = to_query_str(query_args)
        req_url = f"{host}{url}?{query_args_str}"

        body = encrypt_get_setting(self.dev_info)
        x_ladon, x_argus, x_gorgon, x_khronos, x_ss_stub = do_sign_v5(dev_info=self.dev_info,
                                                                      timestamp=timestamp,
                                                                      req_url=req_url,
                                                                      body=body)
        header = {
            "accept-encoding": "gzip",
            "accept": "*/*",
            "x-vc-bdturing-sdk-version": "2.3.7.i18n",
            "sdk-version": "2",
            "x-ss-req-ticket": str(round(time.time() * 1000)),
            "passport-sdk-version": "6010290",
            "x-tt-store-region": self.dev_info['geo']['region'].lower(),
            "x-tt-store-region-src": self.dev_info['extra']['cookies']['store-country-code-src'],
            "user-agent": self.dev_info['extra']['userAgent'],
            "content-type": "application/octet-stream",
            "host": DOMAIN_MSSDK.split('/')[2],
            "connection": "Keep-Alive",
            "cookie": cookie_string(self.dev_info['extra']['cookies']),
            'x-ss-dp': '1233',
            'x-tt-dm-status': 'login=0;ct=1;rt=6',
            'x-tt-request-tag': 't=0;n=1;s=0',
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
        if not resp.cookies:
            pass
        else:
            cookies_dict = cookie_json(resp)
            self.dev_info['extra']['cookies'] = json.loads(json.dumps(cookies_dict, indent=4))
        printf(resp)

        time.sleep(2)
