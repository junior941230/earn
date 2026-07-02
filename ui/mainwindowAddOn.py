from ui.mainwindow import Ui_MainWindow
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from ui.item.switch import AnimatedSwitch
from ui.item.market_state import MarketStateWidget


class MainWindowWithAddOn(Ui_MainWindow):
    def __init__(self):
        super().__init__()
        

    def addAddOn(self):
        container = QWidget()
        container.setFixedHeight(26)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 8, 0)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.switch = AnimatedSwitch()
        self.switch.setFixedSize(40, 20)
        self.switchlabel = QLabel("現貨")
        self.switchlabel.setStyleSheet("color: #ccccff; font-size: 12px;")
        self.market_state_widget = MarketStateWidget()

        layout.addWidget(
            self.market_state_widget,
            alignment=Qt.AlignmentFlag.AlignVCenter,
        )
        layout.addWidget(
            self.switchlabel,
            alignment=Qt.AlignmentFlag.AlignVCenter,
        )
        layout.addWidget(
            self.switch,
            alignment=Qt.AlignmentFlag.AlignVCenter,
        )
        self.tabWidget.setCornerWidget(container, Qt.Corner.TopRightCorner)
