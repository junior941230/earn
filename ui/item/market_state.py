"""Reusable animated switch widget for PyQt6."""
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout
import ntplib
from datetime import datetime, timezone, timedelta
from PyQt6.QtCore import Qt, QTimer, QSize

from PyQt6.QtGui import QIcon


class MarketStateWidget(QWidget):
    """右上角市場狀態顯示元件"""

    def __init__(self, parent=None):
        iconSize = 15
        open_icon = QIcon("ui/green.png")
        self.open_pixmap = open_icon.pixmap(QSize(iconSize, iconSize))
        close_icon = QIcon("ui/red.png")
        self.close_pixmap = close_icon.pixmap(QSize(iconSize, iconSize))
        super().__init__(parent)
        self.setFixedSize(110, 24)
        self.clockClient = ntplib.NTPClient()
        self.timeLabel = QLabel()
        self.timeLabel.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.timeLabel.setStyleSheet("color: #ccccff; font-size: 12px;")
        self.iconLabel = QLabel()
        self.iconLabel.setFixedSize(iconSize, iconSize)
        self.iconLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.addWidget(self.iconLabel)
        layout.addWidget(self.timeLabel, 1)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(500)  # 每秒更新一次時間
        self.update_time()

    def update_time(self):
        response = self.clockClient.request('time.stdtime.gov.tw', version=3)
        tw_tz = timezone(timedelta(hours=8))
        tw_time = datetime.fromtimestamp(response.tx_time, tz=tw_tz)

        closeTime = datetime(tw_time.year, tw_time.month,
                             tw_time.day, 13, 30, tzinfo=tw_tz)
        openTime = datetime(tw_time.year, tw_time.month,
                            tw_time.day, 9, 0, tzinfo=tw_tz)
        if tw_time >= openTime and tw_time < closeTime:
            self.iconLabel.setPixmap(self.open_pixmap)
            self.timeLabel.setText("開盤中 " + tw_time.strftime("%H:%M:%S"))
        else:
            self.iconLabel.setPixmap(self.close_pixmap)
            self.timeLabel.setText("休市中 " + tw_time.strftime("%H:%M:%S"))


if __name__ == "__main__":
    import sys

    from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("Market State Test")
    window.setFixedSize(280, 160)
    window.setStyleSheet("background-color: #13131f;")

    layout = QVBoxLayout(window)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.setSpacing(16)

    test_widget = MarketStateWidget()

    layout.addWidget(test_widget, alignment=Qt.AlignmentFlag.AlignCenter)

    window.show()
    sys.exit(app.exec())
