from ui.watchlist.watchlist import watchlist
from PyQt6.QtWidgets import QGridLayout, QTabWidget
from PyQt6.QtCore import Qt
from database.database import Database
from service.market_data import MarketDataService
from ui.watchlist.watchlistEdit import WatchListEditDialog


class WatchlistController:
    alignMethod = (5, 2)

    def __init__(self, tab, layout: QGridLayout, db: Database, market_data_service: MarketDataService, all_market_data: dict):
        self.tab = tab
        self.layout = layout
        self.db = db
        self.market_data_service = market_data_service
        self.all_market_data = all_market_data
        self.layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)  # 讓卡片靠上排列
        self.watchlistGroups = {}  # {watchlist_id: TargetListWidget}
        self.load_watchlist()

    def edit_watchlistCallback(self, watchlist_id):
        """處理編輯 watchlist 的回調函數"""
        self.current_watchlist_id = watchlist_id
        dialog = WatchListEditDialog(
            self.all_market_data, self.onAddCallback)
        if dialog.exec():
            pass
        self.load_watchlist()

    def onAddCallback(self, name: str, symbol: str):
        self.db.add_watchlist_item(self.current_watchlist_id, symbol)

    def load_watchlist(self):
        """載入 watchlist 資料並更新 UI"""
        watchlists = self.db.get_watchlists()  # 取得所有清單

        for i in range(len(watchlists)):
            cols = self.alignMethod[0]  # 每行幾欄

            wl_id, wl_name = watchlists[i]  # 取得清單 id 與名稱
            self.watchlistGroups[wl_id] = watchlist(
                wl_name, self.edit_watchlistCallback, wl_id)  # 建立 watchlist UI 元件
            for symbol in self.db.get_watchlist_items(wl_id):
                symboldata = self.market_data_service.ApiGetIntradayQuote(
                    symbol)  # 取得即時資料
                self.watchlistGroups[wl_id].add_target(symboldata)
            self.layout.addWidget(
                self.watchlistGroups[wl_id],
                i // cols,   # row
                i % cols     # column
            )
