from ui.watchlist import watchlist
from PyQt6.QtWidgets import QGridLayout, QTabWidget
from PyQt6.QtCore import Qt
from database.database import Database
from service.market_data import MarketDataService


class WatchlistController:
    def __init__(self, tab, layout: QGridLayout, db: Database, market_data_service: MarketDataService):
        self.tab = tab
        self.layout = layout
        self.db = db
        self.market_data_service = market_data_service
        self.layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)  # 讓卡片靠上排列
        self.watchlistGroups = {}  # {watchlist_id: TargetListWidget}
        self.load_watchlist()

    def load_watchlist(self, ):
        """載入 watchlist 資料並更新 UI"""
        watchlists = self.db.get_watchlists() #取得所有清單
        for wl in watchlists: 
            wl_id, wl_name = wl
            self.watchlistGroups[wl_id] = watchlist(wl_name)
            for symbol in self.db.get_watchlist_items(wl_id):
                symboldata = self.market_data_service.ApiGetIntradayQuote(
                    symbol)#取得即時資料
                self.watchlistGroups[wl_id].add_target(symboldata)
            self.layout.addWidget(self.watchlistGroups[wl_id])
