"""Reusable animated switch widget for PyQt6."""

from PyQt6.QtCore import (
    QEasingCurve,
    QRectF,
    Qt,
    QVariantAnimation,
)
from PyQt6.QtGui import QColor, QKeyEvent, QPainter
from PyQt6.QtWidgets import QAbstractButton, QSizePolicy


class AnimatedSwitch(QAbstractButton):
    """A compact, keyboard-accessible switch with a sliding animation.

    ``AnimatedSwitch`` behaves like any checkable Qt button. Connect to its
    inherited ``toggled(bool)`` signal or use ``isChecked()``/``setChecked()``.

    Example::

        switch = AnimatedSwitch(checked=True)
        switch.toggled.connect(lambda enabled: print(enabled))
    """

    def __init__(
        self,
        parent=None,
        *,
        checked: bool = False,
        animation_duration: int = 180,
    ) -> None:
        super().__init__(parent)
        self.setCheckable(True)
        self.setChecked(checked)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedSize(46, 26)

        self._position = 1.0 if checked else 0.0
        self._animation = QVariantAnimation(self)
        self._animation.setDuration(max(0, animation_duration))
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.valueChanged.connect(self._set_position)

        self.toggled.connect(self._animate_to_state)

    def _set_position(self, value: float) -> None:
        self._position = max(0.0, min(1.0, float(value)))
        self.update()

    def _animate_to_state(self, checked: bool) -> None:
        self._animation.stop()
        self._animation.setStartValue(self._position)
        self._animation.setEndValue(1.0 if checked else 0.0)
        self._animation.start()

    def setAnimationDuration(self, milliseconds: int) -> None:
        """Set the slide animation duration in milliseconds."""
        self._animation.setDuration(max(0, milliseconds))

    def animationDuration(self) -> int:
        return self._animation.duration()

    def paintEvent(self, event) -> None:
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        margin = 2.0
        track = QRectF(
            margin,
            margin,
            self.width() - margin * 2,
            self.height() - margin * 2,
        )
        radius = track.height() / 2.0

        off_color = QColor("#2e2e4e")
        on_color = QColor("#5555aa")
        thumb_color = QColor("#e8e8ff")

        if not self.isEnabled():
            off_color.setAlpha(110)
            on_color.setAlpha(110)
            thumb_color.setAlpha(135)

        track_color = self._interpolate_color(
            off_color, on_color, self._position
        )
        painter.setBrush(track_color)
        painter.drawRoundedRect(track, radius, radius)

        thumb_diameter = track.height() - 6.0
        travel = track.width() - thumb_diameter - 6.0
        visual_position = (
            1.0 - self._position
            if self.layoutDirection() == Qt.LayoutDirection.RightToLeft
            else self._position
        )
        thumb_x = track.left() + 3.0 + travel * visual_position
        thumb_y = track.top() + (track.height() - thumb_diameter) / 2.0

        painter.setBrush(thumb_color)
        painter.drawEllipse(
            QRectF(thumb_x, thumb_y, thumb_diameter, thumb_diameter)
        )

        if self.hasFocus():
            focus_color = QColor("#aaaaff")
            focus_color.setAlpha(170)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(focus_color)
            painter.drawRoundedRect(track.adjusted(-1, -1, 1, 1), radius, radius)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.click()
            event.accept()
            return
        super().keyPressEvent(event)

    @staticmethod
    def _interpolate_color(start: QColor, end: QColor, amount: float) -> QColor:
        amount = max(0.0, min(1.0, amount))
        return QColor(
            round(start.red() + (end.red() - start.red()) * amount),
            round(start.green() + (end.green() - start.green()) * amount),
            round(start.blue() + (end.blue() - start.blue()) * amount),
            round(start.alpha() + (end.alpha() - start.alpha()) * amount),
        )


# A shorter alias for call sites that prefer ``Switch()``.
Switch = AnimatedSwitch


__all__ = ["AnimatedSwitch", "Switch"]


if __name__ == "__main__":
    import sys

    from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("Animated Switch Test")
    window.setFixedSize(280, 160)
    window.setStyleSheet("background-color: #13131f;")

    layout = QVBoxLayout(window)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.setSpacing(16)

    status_label = QLabel("狀態：OFF")
    status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    status_label.setStyleSheet("color: #ccccff; font-size: 16px;")

    test_switch = AnimatedSwitch(animation_duration=220)

    def update_status(checked: bool) -> None:
        status_label.setText("狀態：ON" if checked else "狀態：OFF")

    test_switch.toggled.connect(update_status)

    layout.addWidget(status_label)
    layout.addWidget(test_switch, alignment=Qt.AlignmentFlag.AlignCenter)

    window.show()
    sys.exit(app.exec())
