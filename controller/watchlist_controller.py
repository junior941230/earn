from ui.watchlist.watchlist import watchlist, AppendWatchlist
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
        dialog = WatchListEditDialog(
            self.all_market_data, self.onAddCallback, watchlist_id, self.db)
        if dialog.exec():
            pass
        self.load_watchlist()

    def onAddCallback(self, name: str, symbol: str, watchlist_id: int, isExists: bool):
        """處理新增股票的回調函數"""
        if isExists:
            self.db.remove_watchlist_item(watchlist_id, symbol)
        else:
            self.db.add_watchlist_item(watchlist_id, symbol)

    def onReorderCallback(self, watchlist_id: int, symbols: list[str]):
        self.db.set_watchlist_item_order(watchlist_id, symbols)

    def onAddWatchlistCallback(self):
        """處理新增 watchlist 的回調函數"""
        watchlist_id = self.db.add_watchlist("新增清單")
        dialog = WatchListEditDialog(
            self.all_market_data, self.onAddCallback, watchlist_id, self.db)
        if dialog.exec():
            pass
        self.load_watchlist()

    def load_watchlist(self):
        """載入 watchlist 資料並更新 UI"""
        watchlists = self.db.get_watchlists()  # 取得所有清單

        self._clear_watchlist_widgets()
        cols = self.alignMethod[0]  # 每行幾欄
        for i in range(len(watchlists)):

            wl_id, wl_name, wl_sortOrder = watchlists[i]  # 取得清單 id 與名稱
            self.watchlistGroups[wl_id] = watchlist(
                wl_name, self.edit_watchlistCallback, wl_id)  # 建立 watchlist UI 元件
            self.watchlistGroups[wl_id].reorder_callback = self.onReorderCallback
            for symbol in self.db.get_watchlist_items(wl_id):
                symboldata = self.market_data_service.ApiGetIntradayQuote(
                    symbol)  # 取得即時資料
                self.watchlistGroups[wl_id].add_target(symboldata)
            self.layout.addWidget(
                self.watchlistGroups[wl_id],
                i // cols,   # row
                i % cols     # column
            )
        appendWatchlist = AppendWatchlist(self.onAddWatchlistCallback)
        self.layout.addWidget(
            appendWatchlist,
            len(watchlists) // cols,   # row
            len(watchlists) % cols     # column
        )

    def _clear_watchlist_widgets(self):
        """Remove existing widgets before rebuilding the watchlist grid."""
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()  # type: ignore #
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

        self.watchlistGroups.clear()
