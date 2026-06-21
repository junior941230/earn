import json
import requests
from openai import OpenAI
from service.fubon_client import FubonClient
from service.market_data import MarketDataService


class LLMClient:
    def __init__(self):
        with open('key.json') as f:
            keys = json.load(f)
        self.api_key = keys.get('DEEPSEEK_API_KEY')
        self.client = OpenAI(api_key=self.api_key)

    def getWalletBalance(self):
        balanceUrl = "https://api.deepseek.com/user/balance"

        headersConfig = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # 發送 GET 請求
        responseResult = requests.get(balanceUrl, headers=headersConfig)

        # 處理回傳結果
        if responseResult.status_code == 200:
            balanceInfo = responseResult.json()
            return balanceInfo
        else:
            return None

    def smartOrder(self):
        systemPrompt = """你是一個條件單機器人。請根據用戶的指令擷取交易資訊。
        注意：用戶可能會輸入台灣股票名稱的同音錯字或簡稱，請根據你的知識，將其自動推測並校正為正確的「台灣股市上市櫃公司名稱」後再輸出。
        請用json格式回覆，格式如下:
        {
            "action": "buy" 或 "sell",
            "targetName": "股票的中文名稱",
            "price": 用戶設定的價格數值,
            "qty": 用戶設定的數量數值
        }"""

        userPrompt = "金山電的價格低於100元時,買進100股"

        response = self.client.chat.completions.create(
            model="deepseek-chat",  # 注意：目前 DeepSeek API 官方模型名稱通常是 deepseek-chat
            messages=[
                {"role": "system", "content": systemPrompt},
                {"role": "user", "content": userPrompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        return response.choices[0].message.content
