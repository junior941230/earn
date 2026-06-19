import sys
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout,
    QLineEdit, QScrollArea, QWidget, QPushButton,
    QLabel, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont


# ── 單一標的卡片 ──────────────────────────────────────────
class ItemRow(QFrame):
    add_clicked = pyqtSignal(str, str)  # name, symbol

    def __init__(self, data: dict, parent=None):
        super().__init__(parent)
        self.name = data.get("name", "")
        self.symbol = data.get("symbol", "")
        self._build_ui(data)
        self.setObjectName("itemRow")
        self.setFixedHeight(50)

    def _build_ui(self, data: dict):
        name = data.get("name", "")
        symbol = data.get("symbol", "")
        market = data.get("market", "")

        outer = QHBoxLayout(self)
        outer.setContentsMargins(12, 8, 12, 8)
        outer.setSpacing(8)

        # ── + 按鈕 ──
        self.btn_add = QPushButton("+")
        self.btn_add.setFixedSize(22, 22)
        self.btn_add.setObjectName("btnAdd")
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.clicked.connect(
            lambda: self.add_clicked.emit(self.name, self.symbol))

        # ── 內容區 ──

        lbl_name = QLabel(name)
        lbl_name.setObjectName("lblName")
        f_name = QFont("微軟正黑體", 11)
        f_name.setBold(True)
        lbl_name.setFont(f_name)

        lbl_symbol = QLabel(symbol)
        lbl_symbol.setObjectName("lblSymbol")
        lbl_symbol.setFont(QFont("微軟正黑體", 9))

        lbl_market = QLabel(market)
        lbl_market.setObjectName("lblMarket")
        lbl_market.setFont(QFont("微軟正黑體", 9))

        outer.addWidget(lbl_name)
        outer.addWidget(lbl_symbol, alignment=Qt.AlignmentFlag.AlignRight)
        outer.addWidget(lbl_market, alignment=Qt.AlignmentFlag.AlignRight)
        outer.addStretch()

        outer.addWidget(
            self.btn_add,
            alignment=Qt.AlignmentFlag.AlignVCenter
        )

    def enterEvent(self, event):
        self.setProperty("hovered", True)
        self.style().unpolish(self)  # type: ignore #
        self.style().polish(self)  # type: ignore #
        super().enterEvent(event)  # type: ignore #

    def leaveEvent(self, event):
        self.setProperty("hovered", False)
        self.style().unpolish(self)  # type: ignore #
        self.style().polish(self)  # type: ignore #
        super().leaveEvent(event)


# ── 主 Dialog ────────────────────────────────────────────
class WatchListEditDialog(QDialog):
    MAX_VISIBLE_ITEMS = 200

    def __init__(self, items: dict, onAddCallback, parent=None):
        super().__init__(parent)
        self.items = items
        self.onAddCallback = onAddCallback
        self.item_values = list(items.values()) if isinstance(
            items, dict) else list(items)
        self.search_items = [
            (
                item,
                f"{item.get('name', '')} {item.get('symbol', '')}".lower()
            )
            for item in self.item_values
            if isinstance(item, dict)
        ]
        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(120)
        self.search_timer.timeout.connect(self._apply_search)
        self.setWindowTitle("標的搜尋")
        self.setFixedSize(500, 500)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._build_ui()
        self._apply_stylesheet()

    def _build_ui(self):
        # 外層容器（帶圓角背景）
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.container = QFrame()
        self.container.setObjectName("container")
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        root.addWidget(self.container)

        # ── Header ──
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(30)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 0, 8, 0)
        header_layout.setSpacing(0)

        lbl_title = QLabel("＋  新增自選")
        lbl_title.setObjectName("lblTitle")
        f_title = QFont("微軟正黑體", 10)
        f_title.setBold(True)
        lbl_title.setFont(f_title)

        btn_close = QPushButton("✕")
        btn_close.setObjectName("btnClose")
        btn_close.setFixedSize(22, 22)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.clicked.connect(self.reject)

        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        header_layout.addWidget(btn_close)
        container_layout.addWidget(header)

        # ── 搜尋欄 ──
        search_wrap = QFrame()
        search_wrap.setObjectName("searchWrap")
        sw_layout = QHBoxLayout(search_wrap)
        sw_layout.setContentsMargins(10, 8, 10, 8)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("搜尋代號 / 名稱…")
        self.search_box.setFixedHeight(30)
        self.search_box.setObjectName("searchBox")
        self.search_box.textChanged.connect(self._queue_search)
        sw_layout.addWidget(self.search_box)
        container_layout.addWidget(search_wrap)

        # ── 列表 ──
        self.scrollbar = QScrollArea()
        self.scrollbar.setWidgetResizable(True)
        self.scrollbar.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollbar.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.list_container = QWidget()
        self.list_container.setObjectName("listContainer")
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(6, 4, 6, 8)
        self.list_layout.setSpacing(6)
        self.list_layout.addStretch()

        self.scrollbar.setWidget(self.list_container)
        container_layout.addWidget(self.scrollbar)
        self._populate(self.item_values)

    def _populate(self, items: list[dict]):
        self.list_container.setUpdatesEnabled(False)

        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            if item.widget():  # type: ignore #
                item.widget().deleteLater()  # type: ignore #

        for data in list(items)[:self.MAX_VISIBLE_ITEMS]:
            if not isinstance(data, dict):
                continue
            row = ItemRow(data)
            row.add_clicked.connect(self.onAddCallback)
            self.list_layout.insertWidget(
                self.list_layout.count() - 1, row
            )

        self.list_container.setUpdatesEnabled(True)

    def _queue_search(self):
        self.search_timer.start()

    def _apply_search(self):
        kw = self.search_box.text().strip().lower()
        filtered = [
            item for item, searchable_text in self.search_items
            if kw in searchable_text
        ] if kw else self.item_values
        self._populate(filtered)

    def _apply_stylesheet(self):
        self.setStyleSheet("""
            /* ── 外框容器 ── */
            QFrame#container {
                background-color: #1e1e2e;
                border: 1px solid #2e2e4e;
                border-radius: 12px;
            }

            /* ── Header ── */
            QFrame#header {
                background-color: #13131f;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                border-bottom: 1px solid #2e2e4e;
            }
            QLabel#lblTitle {
                color: #ccccff;
                background: transparent;
            }

            /* ── 搜尋區塊 ── */
            QFrame#searchWrap {
                background-color: #1e1e2e;
            }
            QLineEdit#searchBox {
                background-color: #13131f;
                border: 1px solid #2e2e4e;
                border-radius: 6px;
                color: #ccccff;
                padding: 0 10px;
                font-family: 微軟正黑體;
                font-size: 11px;
                selection-background-color: #4444aa;
            }
            QLineEdit#searchBox:focus {
                border-color: #4444aa;
            }
            QLineEdit#searchBox::placeholder {
                color: #555577;
            }

            /* ── 列表背景 ── */
            QWidget#listContainer {
                background-color: #1e1e2e;
            }

            /* ── 標的卡片 ── */
            QFrame#itemRow {
                background-color: #1e1e2e;
                border: 1px solid #2e2e4e;
                border-radius: 8px;
            }
            QFrame#itemRow:hover {
                background-color: #2a2a3e;
                border-color: #5555aa;
            }

            /* ── 文字標籤 ── */
            QLabel#lblName {
                color: #e8e8ff;
                background: transparent;
            }
            QLabel#lblSymbol {
                color: #888888;
                background: transparent;
            }
            QLabel#lblVolume {
                color: #999999;
                background: transparent;
            }

            /* ── + 按鈕 ── */
            QPushButton#btnAdd {
                background-color: transparent;
                color: #aaaaff;
                border: none;
                border-radius: 11px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton#btnAdd:hover {
                background-color: #35355a;
            }
            QPushButton#btnAdd:pressed {
                background-color: #5555aa;
                color: #ffffff;
            }

            /* ── 關閉按鈕 ── */
            QPushButton#btnClose {
                background-color: transparent;
                color: #888888;
                border: none;
                border-radius: 11px;
                font-size: 11px;
            }
            QPushButton#btnClose:hover {
                background-color: #35355a;
                color: #ccccff;
            }
            QPushButton#btnClose:pressed {
                background-color: #5555aa;
            }

            /* ── 捲軸 ── */
            QScrollBar:vertical {
                width: 6px;
                background: #1a1a2e;
                border-radius: 3px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #4444aa;
                border-radius: 3px;
                min-height: 24px;
            }
            QScrollBar::handle:vertical:hover {
                background: #5555aa;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

    # 支援拖曳移動（無邊框視窗）
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, '_drag_pos'):
            self.move(event.globalPosition().toPoint() - self._drag_pos)


# ── 範例資料 ─────────────────────────────────────────────
SAMPLE_ITEMS = [
    {"title": "台積電",   "symbol": "2330", "market": "台灣"},
    {"title": "鴻海",     "symbol": "2317", "market": "台灣"},
    {"title": "聯發科",   "symbol": "2454", "market": "台灣"},
    {"title": "蘋果",     "symbol": "AAPL", "market": "美國"},
    {"title": "輝達",     "symbol": "NVDA", "market": "美國"},
    {"title": "特斯拉",   "symbol": "TSLA", "market": "美國"},
    {"title": "微軟",     "symbol": "MSFT", "market": "美國"},
    {"title": "中華電信", "symbol": "2412", "market": "台灣"},
    {"title": "國泰金",   "symbol": "2882", "market": "台灣"},
    {"title": "富邦金",   "symbol": "2881", "market": "台灣"},
]

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("微軟正黑體", 10))
    dlg = WatchListEditDialog(SAMPLE_ITEMS)
    dlg.exec()
