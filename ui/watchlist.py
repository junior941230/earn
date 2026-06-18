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
        'name'       : '台積電',
        'code'       : '2330',
        'price'      : 950.0,
        'change'     : 12.5,
        'change_pct' : 1.33,
        'volume'     : '125,430',
        'extra'      : '半導體'
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
        

        self.lbl_code = QLabel(self.data.get('code', '--'))
        self.lbl_code.setFont(QFont('微軟正黑體', 9))
        self.lbl_code.setStyleSheet("color: #888888;")

        self.lbl_price = QLabel(f"{self.data.get('price', 0):.2f}")
        self.lbl_price.setFont(QFont('微軟正黑體', 13, QFont.Weight.Bold))
        self.lbl_price.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        change = self.data.get('change', 0)
        change_pct = self.data.get('change_pct', 0)
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
        top_row.addWidget(self.lbl_code)
        top_row.addStretch()
        top_row.addWidget(self.lbl_change)
        top_row.addWidget(self.lbl_price)

        # ── 第二行：成交量 ──
        vol_text = f"量  {self.data.get('volume', '--')}"
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
                if item.widget():
                    item.widget().deleteLater()
        self._build_ui()
        self._apply_style()


class watchlist(QFrame):
    def __init__(self, watchlistName, parent=None):
        self.watchlistName = watchlistName
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
        header.setFixedHeight(44)
        header.setObjectName("Header")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(12, 0, 12, 0)

        title = QLabel(self.watchlistName)
        title.setFont(QFont('微軟正黑體', 10, QFont.Weight.Bold))
        title.setStyleSheet("color: #ccccff;")

        self.lbl_count = QLabel("0 檔")
        self.lbl_count.setFont(QFont('微軟正黑體', 9))
        self.lbl_count.setStyleSheet("color: #888888;")
        self.lbl_count.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        h_layout.addWidget(title)
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
        code = data.get('code', '')
        if code in self._cards:
            self._cards[code].refresh(data)
        else:
            card = TargetCard(data)
            self._cards[code] = card
            idx = self.card_layout.count() - 1   # stretch 前插入
            self.card_layout.insertWidget(idx, card)
            self._update_count()

    def remove_target(self, code: str):
        """移除指定代號的標的卡片"""
        if code in self._cards:
            card = self._cards.pop(code)
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
        'code': '2330',
        'price': 950.0,
        'change': 12.5,
        'change_pct': 1.33,
        'volume': '125,430',
        'extra': '半導體'
    })
    watchlist_widget.add_target({
        'name': '聯發科',
        'code': '2454',
        'price': 600.0,
        'change': -5.0,
        'change_pct': -0.83,
        'volume': '98,210',
        'extra': 'IC 設計'
    })
    watchlist_widget.show()
    sys.exit(app.exec())
