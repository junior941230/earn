from PyQt6.QtWidgets import QMainWindow
from ui.mainwindow import Ui_MainWindow
from database.database import Database
from service.fubon_client import FubonClient
from service.market_data import MarketDataService
from controller.watchlist_controller import WatchlistController


class MainWindowController(QMainWindow):
    def __init__(self):
        super().__init__()

        self.db = Database()
        self.fubon_client = FubonClient()
        self.fubon_client.connect()
        self.market_data_service = MarketDataService(self.fubon_client)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.watchlist_controller = WatchlistController(
            tab=self.ui.watchlistTab,
            layout=self.ui.watchlistsLayout,
            db=self.db, market_data_service=self.market_data_service
        )

        # 之後可以繼續加：
        # self.smart_controller = SmartController(self.ui.smartTab)
        # self.strong_trade_controller = StrongTradeController(self.ui.strongTradeTab)
        # self.chart_controller = ChartController(self.ui.chartTab)

    def closeEvent(self, event):
        # 在視窗關閉前，確保資料庫連線被正確關閉
        print("Closing service...")
        self.db.close()
        self.market_data_service.disconnect()
        super().closeEvent(event)
