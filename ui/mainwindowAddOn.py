from mainwindow import Ui_MainWindow
from PyQt6.QtCore import Qt
from ui.item.switch import AnimatedSwitch


def addAddonToMainWindow(main_window: Ui_MainWindow):
    switch = AnimatedSwitch()
    main_window.tabWidget.setCornerWidget(switch, Qt.Corner.TopRightCorner)
    