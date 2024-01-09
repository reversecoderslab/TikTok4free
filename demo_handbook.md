### English version

# Demo Handbook / Demo

## Forward

Presently, we provide a complete demo (platform device registration and activation) for the users to do some test of our service. And to launch the demo successfully you should apply for a free test key from us by requesting on RapidAPI https://rapidapi.com/reversecoders/api/tiktok4free/pricing.

## Step

1. `git clone https://gitlab.com/reversecoders/TikTok4free.git` 
2. `cd TikTok4free/demo`
3. replace the key of key.py with the test key applied from us.
4. `python3 main.py` # launch the android/ios device register and activation demo, you can get an device_id and install_id
5. you can change the device info and app info by yourself to generate new did and iid;
6. have fun!

In this demo, we supported 4 core risk control apis of 3 core biz scenarios, covering Tiktok's current strongest risk control scenario:
* General scenario:
    * core signature api `do_sign_v5`: get the signature result, such as x_ladon, x_argus, x_gorgon, x_khronos;
* Device template getting: `DeviceRegister.process_dev_info("android")` in demo
    * get devive tenplate api `do_get_dev_tmpl`: get the device template, android, from our server. Device fingerprints are the core of risk control countermeasures, and many interfaces are strongly correlated. Therefore, in order to reduce the difficulty of analyzing and understanding device fingerprints, and to avoid filling different device fingerprint data through different interfaces, which may cause risk control , we directly return the general device template through this interface, you only need to fill in the correct value as needed.
* Device register:`DeviceRegister.post_device_register()` in demo
    * Device registration request body Encryption API `get_device_register_body`: Connotation `tt_encrypt` API(**Deprecated**), user only needs to send the correct device fingerprint template, which filled in correct value, as a parameter to the API. We automatically complete the complex format conversion as well as body encryption.
* Device activate:  `DeviceRegister.send_app_alert_check()` in demo
* Sec device token getting: `DeviceRegister.get_token()` in demo
    * SecDeviceToken encrypt interface `encrypt_get_token`: encrypt the device fingerprint to get the correct request body of `sdi/get_token`. The parameter is the same as `get_device_register_body`;
    * SecDeviceToken decrypt interface `decrypt_get_token`: decrypt the response from `sdi/get_token`, you can get the important `token` from the result.
* Risk Info Report: `DeviceRegister.post_ri_report()` in demo.

Finally, you can get three important id:
* device id
* install id
* sec device token
* risk information report

### 英文版

# 演示手册/演示

## 向前

目前，我们提供了完整的演示（平台设备注册和激活）供用户对我们的服务进行一些测试。 要成功启动演示，您应该通过 RapidAPI https://rapidapi.com/reversecoders/api/tiktok4free/pricing 请求，向我们申请免费测试密钥。

## 步

1. `git 克隆 https://gitlab.com/reversecoders/TikTok4free.git`
2.`cd TikTok4free/演示`
3.将key.py中的密钥替换为我们申请的测试密钥。
4. `python3 main.py` # 启动android/ios设备注册和激活demo，可以获得device_id和install_id
5.您可以自行更改设备信息和应用程序信息，生成新的did和iid；
6.玩得开心！

在本次demo中，我们支持了3个核心业务场景的4个核心风控API，覆盖了抖音目前最强的风控场景：
* 一般场景：
     * 核心签名api `do_sign_v5`：获取签名结果，如x_ladon、x_argus、x_gorgon、x_khronos；
* 设备模板获取：demo中`DeviceRegister.process_dev_info("android")`
     * get devive tenplate api `do_get_dev_tmpl`：从我们的服务器获取设备模板 android。 设备指纹是风控对策的核心，很多接口都是强关联的。 因此，为了降低分析和理解设备指纹的难度，也避免通过不同的接口填写不同的设备指纹数据，可能造成风险控制，我们通过该接口直接返回通用的设备模板，您只需填写即可 根据需要设置正确的值。
* 设备注册：demo中`DeviceRegister.post_device_register()`
     * 设备注册请求体 加密API `get_device_register_body`：内涵`tt_encrypt` API（**已弃用**），用户只需将填写正确值的正确设备指纹模板作为参数发送给API即可。 我们自动完成复杂的格式转换以及正文加密。
* 设备激活：演示中的`DeviceRegister.send_app_alert_check()`
* Sec 设备令牌获取：demo 中的`DeviceRegister.get_token()`
     * SecDeviceToken加密接口`encrypt_get_token`：对设备指纹进行加密，得到正确的请求体`sdi/get_token`。 参数与`get_device_register_body`相同；
     * SecDeviceToken解密接口`decrypt_get_token`：解密`sdi/get_token`的响应，从结果中可以得到重要的`token`。
* 风险信息报告：演示中的“DeviceRegister.post_ri_report()”。

最后可以得到三个重要的id：
* 设备ID
* 安装ID
* 秒设备令牌
* 风险信息报告
