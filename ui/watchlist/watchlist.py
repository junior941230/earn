import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QScrollArea, QFrame, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor


class TargetCard(QFrame):
    """
    單一標的的資訊卡片
    data = {
        'name'                  : '台積電',
        'symbol'                : '2330',
        'closePrice'        : 950.0,
        'change'                : 12.5,
        'changePercent'         : 1.33,
        "total" {'tradeVolume'  : '125,430'},
        'extra'                 : '半導體'
    }
    """

    def __init__(self, data: dict, parent=None):
        super().__init__(parent)
        self.data = data
        self._build_ui()
        self._apply_style()

    def _build_ui(self):
        self.setFixedHeight(90)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 8, 12, 8)
        main_layout.setSpacing(4)

        # ── 第一行：名稱 + 代號 + 價格 ──
        top_row = QHBoxLayout()

        self.lbl_name = QLabel(self.data.get('name', '--'))
        self.lbl_name.setFont(QFont('微軟正黑體', 11, QFont.Weight.Bold))

        self.lbl_symbol = QLabel(self.data.get('symbol', '--'))
        self.lbl_symbol.setFont(QFont('微軟正黑體', 9))
        self.lbl_symbol.setStyleSheet("color: #888888;")

        self.lbl_price = QLabel(f"{self.data.get('closePrice', 0):.2f}")
        self.lbl_price.setFont(QFont('微軟正黑體', 13, QFont.Weight.Bold))
        self.lbl_price.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        change = self.data.get('change', 0)
        change_pct = self.data.get('changePercent', 0)
        sign = '+' if change >= 0 else ''
        change_str = f"{sign}{change:.2f}  ({sign}{change_pct:.2f}%)"

        self.lbl_change = QLabel(change_str)
        self.lbl_change.setFont(QFont('微軟正黑體', 9, QFont.Weight.Bold))
        self.lbl_change.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        # 漲跌顏色（台股：漲紅跌綠）
        color = "#e74c3c" if change >= 0 else "#2ecc71"
        self.lbl_change.setStyleSheet(f"color: {color};")
        self.lbl_price.setStyleSheet(f"color: {color};")

        top_row.addWidget(self.lbl_name)
        top_row.addWidget(self.lbl_symbol)
        top_row.addStretch()
        top_row.addWidget(self.lbl_change)
        top_row.addWidget(self.lbl_price)

        # ── 第二行：成交量 ──
        vol_text = f"量  {self.data.get('total', {}).get('tradeVolume', '--')}"
        self.lbl_vol = QLabel(vol_text)
        self.lbl_vol.setFont(QFont('微軟正黑體', 8))
        self.lbl_vol.setStyleSheet("color: #999999;")

        main_layout.addLayout(top_row)
        main_layout.addWidget(self.lbl_vol)

    def _apply_style(self):
        self.setObjectName("TargetCard")
        self.setStyleSheet("""
            QFrame#TargetCard {
                background-color: #1e1e2e;
                border: 1px solid #2e2e4e;
                border-radius: 8px;
            }
            QFrame#TargetCard:hover {
                background-color: #2a2a3e;
                border: 1px solid #5555aa;
            }
            QFrame#TargetCard QLabel {
                background-color: transparent;  /* ← 加這行 */
            }
        """)

    def refresh(self, data: dict):
        """動態更新卡片資料（清除舊 layout 重建）"""
        self.data = data
        # 清除舊有 layout 內容
        old_layout = self.layout()
        if old_layout:
            while old_layout.count():
                item = old_layout.takeAt(0)
                if item.widget(): # type: ignore
                    item.widget().deleteLater()  # type: ignore
        self._build_ui()
        self._apply_style()


class watchlist(QFrame):
    def __init__(self, watchlistName, edit_callback, wl_id, parent=None):
        self.watchlistName = watchlistName
        self.edit_callback = edit_callback
        self.wl_id = wl_id
        super().__init__(parent)
        self._cards: dict[str, TargetCard] = {}
        self._build_ui()
        self._apply_style()

    def _build_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # ── 標題列 ──
        header = QFrame()
        header.setFixedHeight(30)
        header.setObjectName("Header")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(12, 0, 12, 0)

        title = QLabel(self.watchlistName)
        title.setFont(QFont('微軟正黑體', 10, QFont.Weight.Bold))
        title.setStyleSheet("color: #ccccff;")

        self.btn_edit = QPushButton("✏️")
        self.btn_edit.setObjectName("EditButton")
        self.btn_edit.setFixedSize(22, 22)
        self.btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_edit.setToolTip("編輯清單")
        self.btn_edit.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.lbl_count = QLabel("0 檔")
        self.lbl_count.setFont(QFont('微軟正黑體', 9))
        self.lbl_count.setStyleSheet("color: #888888;")
        self.lbl_count.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.btn_edit.clicked.connect(
            lambda: self.edit_callback(self.wl_id))

        h_layout.addWidget(title)
        h_layout.addWidget(self.btn_edit)
        h_layout.addStretch()
        h_layout.addWidget(self.lbl_count)

        # ── 捲動區域 ──
        self.scrollBar = QScrollArea()
        self.scrollBar.setWidgetResizable(True)
        self.scrollBar.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scrollBar.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.scrollBar.setFrameShape(QFrame.Shape.NoFrame)

        # 卡片容器
        self.container = QWidget()
        self.card_layout = QVBoxLayout(self.container)
        self.card_layout.setContentsMargins(8, 8, 8, 8)
        self.card_layout.setSpacing(6)
        self.card_layout.addStretch()  # 卡片靠上排列

        self.scrollBar.setWidget(self.container)

        outer_layout.addWidget(header)
        outer_layout.addWidget(self.scrollBar)
        self.setMaximumWidth(300)  # 限制最大寬度，讓 UI 看起來更緊湊
        self.setMaximumHeight(500)  # 限制最大高度，避免過長的清單占滿整個視窗

    def _apply_style(self):
        self.setObjectName("TargetListWidget")
        self.setStyleSheet("""
            QFrame#TargetListWidget {
                background-color: #13131f;
                border: 1px solid #4444aa;       /* ← 外框線條顏色 */
                border-radius: 12px;             /* ← 圓角程度 */
            }
            QFrame#Header {
                background-color: #13131f;
                border: none;
                border-bottom: 1px solid #2e2e4e;
                border-radius: 0px;
            }
            QFrame#TargetListWidget QPushButton#EditButton {
                background-color: transparent;
                border: none;
                color: #aaaaff;
                font-size: 14px;
                font-weight: bold;
                padding: 0px;
            }
            QFrame#TargetListWidget QPushButton#EditButton:hover {
                color: #ffffff;
                background-color: #35355a;
                border-radius: 11px;
            }
            QFrame#TargetListWidget QPushButton#EditButton:pressed {
                background-color: #5555aa;
            }
            QScrollArea {
                background-color: #13131f;
                border: none;                    /* ← 避免 ScrollArea 自己也畫框 */
            }
            QWidget {
                background-color: #13131f;
            }
            QScrollBar:vertical {
                background: #1a1a2e;
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #4444aa;
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

    def add_target(self, data: dict):
        """新增標的；若代號已存在則更新資料"""
        symbol = data.get('symbol', '')
        if symbol in self._cards:
            self._cards[symbol].refresh(data)
        else:
            card = TargetCard(data)
            self._cards[symbol] = card
            idx = self.card_layout.count() - 1   # stretch 前插入
            self.card_layout.insertWidget(idx, card)
            self._update_count()

    def remove_target(self, symbol: str):
        """移除指定代號的標的卡片"""
        if symbol in self._cards:
            card = self._cards.pop(symbol)
            self.card_layout.removeWidget(card)
            card.deleteLater()
            self._update_count()

    def clear_all(self):
        """清除全部標的"""
        for card in self._cards.values():
            self.card_layout.removeWidget(card)
            card.deleteLater()
        self._cards.clear()
        self._update_count()

    def _update_count(self):
        self.lbl_count.setText(f"{len(self._cards)} 檔")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    watchlist_widget = watchlist("Test Watchlist")
    watchlist_widget.add_target({
        'name': '台積電',
        'symbol': '2330',
        'closePrice': 950.0,
        'change': 12.5,
        'changePercent': 1.33,
        'tradeVolume': '125,430',
        'extra': '半導體'
    })
    watchlist_widget.add_target({
        'name': '聯發科',
        'symbol': '2454',
        'closePrice': 600.0,
        'change': -5.0,
        'changePercent': -0.83,
        'tradeVolume': '98,210',
        'extra': 'IC 設計'
    })
    watchlist_widget.show()
    sys.exit(app.exec())
