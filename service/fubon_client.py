# 檔案用途：集中管理富邦 Neo SDK；之後放登入、登出、取得 SDK client。
from fubon_neo.sdk import FubonSDK
import json


class FubonClient:
    def __init__(self):
        with open("key.json", "r") as f:
            key = json.load(f)
            self.sdk = FubonSDK()
            self.accounts = self.sdk.login(key["ID"], key["PASSWORD"],
                                           key["CERT_PATH"])  # 需登入後，才能取得行情權限

    def connect(self):
        self.sdk.init_realtime()  # 建立行情連線

    def getSDK(self):
        return self.sdk
