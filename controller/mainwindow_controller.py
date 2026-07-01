from PyQt6.QtWidgets import QMainWindow
from ui.mainwindow import Ui_MainWindow
from database.database import Database
from service.fubon_client import FubonClient
from service.market_data import MarketDataService
from service.websocket_manerger import WebSocketManager
from controller.watchlist_controller import WatchlistController
from PyQt6.QtGui import QIcon


class MainWindowController(QMainWindow):
    def __init__(self):
        super().__init__()

        self.db = Database()
        self.db.initTables()
        self.fubon_client = FubonClient()
        self.fubon_client.connect()
        self.market_data_service = MarketDataService(self.fubon_client)
        self.websocket_manager = WebSocketManager(self.market_data_service)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.all_market_data = self.generateAllMarketData()

        self.watchlist_controller = WatchlistController(
            tab=self.ui.watchlistTab,
            layout=self.ui.watchlistsLayout,
            db=self.db, market_data_service=self.market_data_service,
            websocket_manager=self.websocket_manager,
            all_market_data=self.all_market_data
        )

        # 之後可以繼續加：
        # self.smart_controller = SmartController(self.ui.smartTab)
        # self.strong_trade_controller = StrongTradeController(self.ui.strongTradeTab)
        # self.chart_controller = ChartController(self.ui.chartTab)

        self.setWindowTitle("earn")
        icon = QIcon("ui/icon.png")  # 替換為你的圖標路徑
        self.setWindowIcon(icon)

    def generateAllMarketData(self):
        OTC_data = self.market_data_service.ApiSnapshotQuote("OTC")
        TSE_data = self.market_data_service.ApiSnapshotQuote("TSE")
        all_market_data = {}
        all_market_data.update(self._add_market_type(OTC_data, "上櫃"))
        all_market_data.update(self._add_market_type(TSE_data, "上市"))
        return all_market_data

    def _add_market_type(self, market_data, market_type):
        """替快照資料中的每個標的補上市場類型。"""
        quotes = self._extract_quotes(market_data)
        result = {}

        for quote in quotes:
            if not isinstance(quote, dict):
                continue

            symbol = quote.get("symbol")
            if not symbol:
                continue

            item = quote.copy()
            item["market"] = market_type
            result[symbol] = item

        return result

    def _extract_quotes(self, market_data):
        if market_data is None:
            return []

        if isinstance(market_data, list):
            return market_data

        if isinstance(market_data, dict):
            for key in ("data", "quotes", "items"):
                quotes = market_data.get(key)
                if isinstance(quotes, list):
                    return quotes

            return [market_data]

        return []

    def closeEvent(self, event):
        # 在視窗關閉前，確保資料庫連線被正確關閉
        print("Closing service...")
        self.db.close()
        self.market_data_service.disconnect()
        super().closeEvent(event)
