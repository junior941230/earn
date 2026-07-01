# Please install OpenAI SDK first: `pip3 install openai`
import json
import requests
from openai import OpenAI
from service.fubon_client import FubonClient
from service.market_data import MarketDataService

# Load API key from key.json
with open('key.json') as f:
    keys = json.load(f)

# balanceUrl = "https://api.deepseek.com/user/balance"

# headersConfig = {
#     "Accept": "application/json",
#     "Authorization": f"Bearer {keys['DEEPSEEK_API_KEY']}"
# }

# # 發送 GET 請求
# responseResult = requests.get(balanceUrl, headers=headersConfig)

# # 處理回傳結果
# if responseResult.status_code == 200:
#     balanceInfo = responseResult.json()
#     print("查詢成功，餘額詳細資訊如下：")
#     print(balanceInfo)
# else:
#     print("查詢失敗，HTTP 狀態碼：", responseResult.status_code)
#     print("錯誤訊息：", responseResult.text)


def _extractQuotes(marketData):
    if not marketData:
        return []

    if isinstance(marketData, list):
        return marketData

    if isinstance(marketData, dict):
        for dictKey in ("data", "quotes", "items"):
            foundQuotes = marketData.get(dictKey)
            if isinstance(foundQuotes, list):
                return foundQuotes
        return [marketData]

    return []


def _addMarketType(marketData):
    extractedQuotes = _extractQuotes(marketData)
    formattedResult = []

    for singleQuote in extractedQuotes:
        # 合併型別與 EQUITY 判斷
        if not isinstance(singleQuote, dict) or singleQuote.get("type") != "EQUITY":
            continue

        stockSymbol = singleQuote.get("symbol")

        # 合併字串有效性、是否全為數字，以及長度與開頭規則的過濾條件
        if (not stockSymbol or
            not stockSymbol.isdigit() or
                (not stockSymbol.startswith("00") and len(stockSymbol) == 5)):
            continue

        stockName = singleQuote.get("name", "")
        formattedResult.append((stockName, stockSymbol))

    return formattedResult


fubonClient = FubonClient()
fubonClient.connect()
marketDataService = MarketDataService(fubonClient)
marketDataService.disconnect()
otcData = marketDataService.ApiSnapshotQuote("OTC")
tseData = marketDataService.ApiSnapshotQuote("TSE")

allMarketData = []
allMarketData.extend(_addMarketType(otcData))
allMarketData.extend(_addMarketType(tseData))

csvHeader = "name,symbol\n"
compressedMarketString = csvHeader + \
    "\n".join([f"{name},{symbol}" for name, symbol in allMarketData])

client = OpenAI(
    api_key=keys["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com"
)

# 加上 f 前綴，並將 JSON 的 {} 替換為 {{}}
systemPrompt = """你是一個條件單機器人。請根據用戶的指令擷取交易資訊。
注意：用戶可能會輸入台灣股票名稱的同音錯字或簡稱，請根據你的知識，將其自動推測並校正為正確的「台灣股市上市櫃公司名稱」後再輸出。
如果是用戶未提及的資料請填入NONE，請勿自行推測。
請用json格式回覆，格式如下:
{
    "action": "buy" 或 "sell",
    "targetName": "股票的中文名稱",
    "price": 用戶設定的價格數值,
    "qty": 用戶設定的數量數值
}"""

userPrompt = "金山電的價格低於100元,買進數量100股"

response = client.chat.completions.create(
    model="deepseek-chat",  # 注意：目前 DeepSeek API 官方模型名稱通常是 deepseek-chat
    messages=[
        {"role": "system", "content": systemPrompt},
        {"role": "user", "content": userPrompt},
    ],
    response_format={"type": "json_object"},
    temperature=0.1
)

print(response.choices[0].message.content)
print(f"輸入消耗 (Prompt): {response.usage.prompt_tokens}")
print(f"輸出消耗 (Completion): {response.usage.completion_tokens}")
print(f"總共消耗 (Total): {response.usage.total_tokens}")
