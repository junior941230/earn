# 檔案用途：集中處理行情；之後放 WebSocket 連線、訂閱、報價 callback。
if __package__ in (None, ""):
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from service.fubon_client import FubonClient
from fubon_neo.fugle_marketdata.rest.base_rest import FugleAPIError


def wait_for_shutdown():
    try:
        while True:
            input("WebSocket is running. Press Ctrl+C or Ctrl+D to stop.\n")
    except (KeyboardInterrupt, EOFError):
        print("\nStopping WebSocket...")


class MarketDataService:
    ALL_STOCK_MARKETS = ("TSE", "OTC")
    ALL_STOCK_STATUS_FILTERS = ("isNormal", "isAttention", "isDisposition")

    def __init__(self, fubon_client: FubonClient):
        # 初始化行情服務，例如建立 WebSocket 連線等
        self.fubon_client = fubon_client
        self.reststock = self.fubon_client.getSDK().marketdata.rest_client.stock
        self.WebSocketStock = self.fubon_client.getSDK().marketdata.websocket_client.stock
        self.WebSocketStock.on('message', self._handle_websocket_message)
        self.WebSocketStock.connect()
        self._is_websocket_connected = True

    def ApiGetIntradayTickers(self, exchange):
        try:
            return self.reststock.intraday.tickers(type='EQUITY', exchange=exchange, isNormal=True, isAttention=True, isDisposition=True)
        except FugleAPIError as e:
            self._print_api_error(e)
            return None

    def ApiGetIntradayTicker(self, symbol):
        try:
            return self.reststock.intraday.ticker(symbol=symbol)
        except FugleAPIError as e:
            self._print_api_error(e)
            return None

    def ApiGetIntradayQuote(self, symbol):
        try:
            return self.reststock.intraday.quote(symbol=symbol)
        except FugleAPIError as e:
            self._print_api_error(e)
            return None

    def ApiGetIntradayCandles(self, symbol):
        try:
            return self.reststock.intraday.candles(symbol=symbol)
        except FugleAPIError as e:
            self._print_api_error(e)
            return None

    def ApiGetIntradayTrades(self, symbol):
        try:
            return self.reststock.intraday.trades(symbol=symbol)
        except FugleAPIError as e:
            self._print_api_error(e)
            return None

    def ApiGetIntradayVolumes(self, symbol):
        try:
            return self.reststock.intraday.volumes(symbol=symbol)
        except FugleAPIError as e:
            self._print_api_error(e)
            return None

    def ApiSnapshotQuote(self, market):
        try:
            return self.reststock.snapshot.quotes(market=market)
        except FugleAPIError as e:
            self._print_api_error(e)
            return None

    def ApiSnapshotMovers(self, market, direction='up', change='percent'):
        try:
            return self.reststock.snapshot.movers(market=market, direction=direction, change=change)
        except FugleAPIError as e:
            self._print_api_error(e)
            return None

    def ApiSnapshotActives(self, market, trade='value'):
        try:
            return self.reststock.snapshot.actives(market=market, trade=trade)
        except FugleAPIError as e:
            self._print_api_error(e)
            return None

    def ApiGetHistoricalCandles(self, symbol, start_date, end_date):
        request = {"symbol": symbol, "from": start_date, "to": end_date}
        try:
            return self.reststock.historical.candles(**request)
        except FugleAPIError as e:
            self._print_api_error(e)
            return None

    def ApiGetHistoricalStats(self, symbol):
        try:
            return self.reststock.historical.stats(symbol=symbol)
        except FugleAPIError as e:
            self._print_api_error(e)
            return None

    def ApiGetTechnicalSMA(self, symbol, start_date, end_date, timeframe, period):
        request = {"symbol": symbol, "from": start_date,
                   "to": end_date, "timeframe": timeframe, "period": period}
        try:
            return self.reststock.technical.sma(**request)
        except FugleAPIError as e:
            self._print_api_error(e)
            return None

    def ApiGetTechnicalRSI(self, symbol, start_date, end_date, timeframe, period):
        request = {"symbol": symbol, "from": start_date,
                   "to": end_date, "timeframe": timeframe, "period": period}
        try:
            return self.reststock.technical.rsi(**request)
        except FugleAPIError as e:
            self._print_api_error(e)
            return None

    def ApiGetTechnicalKDJ(self, symbol, start_date, end_date, timeframe, rPeriod, kPeriod, dPeriod):
        request = {"symbol": symbol, "from": start_date, "to": end_date,
                   "timeframe": timeframe, "rPeriod": rPeriod, "kPeriod": kPeriod, "dPeriod": dPeriod}
        try:
            return self.reststock.technical.kdj(**request)
        except FugleAPIError as e:
            self._print_api_error(e)
            return None

    def ApiGetTechnicalMACD(self, symbol, start_date, end_date, timeframe, fast, slow, signal):
        request = {"symbol": symbol, "from": start_date, "to": end_date,
                   "timeframe": timeframe, "fast": fast, "slow": slow, "signal": signal}
        try:
            return self.reststock.technical.macd(**request)
        except FugleAPIError as e:
            self._print_api_error(e)
            return None

    def ApiGetTechnicalBBANDS(self, symbol, start_date, end_date, timeframe, period):
        request = {"symbol": symbol, "from": start_date,
                   "to": end_date, "timeframe": timeframe, "period": period}
        try:
            return self.reststock.technical.bb(**request)
        except FugleAPIError as e:
            self._print_api_error(e)
            return None

    def _handle_websocket_message(self, message):
        # 處理 WebSocket 訊息的邏輯
        print("Received WebSocket message:", message)

    def WebSocketSubscribe(self, channel, symbol):
        # 訂閱 WebSocket 報價
        request = {"channel": channel, "symbol": symbol}
        self.WebSocketStock.subscribe(request)

    def WebSocketUnsubscribe(self, channel, symbol):
        # 取消訂閱 WebSocket 報價
        request = {"channel": channel, "symbol": symbol}
        self.WebSocketStock.unsubscribe(request)

    def _print_api_error(self, error):
        print(f"Error: {error}")
        print("------------")
        print(f"Status Code: {error.status_code}")  # 例: 429
        # 例: {"statusCode":429,"message":"Rate limit exceeded"}
        print(f"Response Text: {error.response_text}")

    def disconnect(self):
        # 斷開 WebSocket 連線
        if not getattr(self, "_is_websocket_connected", False):
            return

        self.WebSocketStock.disconnect()
        self._is_websocket_connected = False


if __name__ == "__main__":
    fubon_client = FubonClient()
    fubon_client.connect()
    market_data_service = MarketDataService(fubon_client)
    try:
        market_data_service.WebSocketSubscribe(
            channel='stock', symbol='2330')
        wait_for_shutdown()
    finally:
        market_data_service.disconnect()
