from PyQt5.QtWidgets import (
    QApplication,
    QSizePolicy,
    QWidget,
    QSlider,
    QHBoxLayout,
    QLabel,
)
from PyQt5.QtCore import Qt, QRect, QSize
from PyQt5.QtGui import QPainter, QBrush, QPalette, QPaintEvent, QMouseEvent
from PyQt5.QtWidgets import QStyle, QStyleOptionSlider
from PyQt5.QtCore import pyqtSignal

class RangeSlider(QWidget):
    valueChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.first_position = 1
        self.second_position = 8
        self._first_sc = None
        self._second_sc = None

        self.opt = QStyleOptionSlider()
        self.opt.minimum = 0
        self.opt.maximum = 10

        self.setTickPosition(QSlider.TicksAbove)
        self.setTickInterval(1)

        self.setSizePolicy(
            QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed, QSizePolicy.Slider)
        )

    def setRangeLimit(self, minimum: int, maximum: int):
        self.opt.minimum = minimum
        self.opt.maximum = maximum
        self.update()

    def setRange(self, start: int, end: int):
        self.first_position = max(self.opt.minimum, min(start, end))
        self.second_position = min(self.opt.maximum, max(start, end))
        self.update()
        self.valueChanged.emit()

    def getRange(self):
        return (self.first_position, self.second_position)

    def setTickPosition(self, position: QSlider.TickPosition):
        self.opt.tickPosition = position

    def setTickInterval(self, ti: int):
        self.opt.tickInterval = ti

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)

        # Draw rule
        self.opt.initFrom(self)
        self.opt.rect = self.rect()
        self.opt.sliderPosition = 0
        self.opt.subControls = QStyle.SC_SliderGroove | QStyle.SC_SliderTickmarks

        # Draw GROOVE
        self.style().drawComplexControl(QStyle.CC_Slider, self.opt, painter)

        # Draw INTERVAL
        color = self.palette().color(QPalette.Highlight)
        color.setAlpha(160)
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)

        self.opt.sliderPosition = self.first_position
        x_left_handle = (
            self.style()
            .subControlRect(QStyle.CC_Slider, self.opt, QStyle.SC_SliderHandle)
            .center()
            .x()
        )

        self.opt.sliderPosition = self.second_position
        x_right_handle = (
            self.style()
            .subControlRect(QStyle.CC_Slider, self.opt, QStyle.SC_SliderHandle)
            .center()
            .x()
        )

        groove_rect = self.style().subControlRect(
            QStyle.CC_Slider, self.opt, QStyle.SC_SliderGroove
        )

        selection = QRect(
            x_left_handle,
            groove_rect.y(),
            x_right_handle - x_left_handle,
            groove_rect.height(),
        ).adjusted(-1, 1, 1, -1)

        painter.drawRect(selection)

        # Draw first handle
        self.opt.subControls = QStyle.SC_SliderHandle
        self.opt.sliderPosition = self.first_position
        self.style().drawComplexControl(QStyle.CC_Slider, self.opt, painter)

        # Draw second handle
        self.opt.sliderPosition = self.second_position
        self.style().drawComplexControl(QStyle.CC_Slider, self.opt, painter)

    def mousePressEvent(self, event: QMouseEvent):
        event.accept()

        self.opt.sliderPosition = self.first_position
        self._first_sc = self.style().hitTestComplexControl(
            QStyle.CC_Slider, self.opt, event.pos(), self
        )

        self.opt.sliderPosition = self.second_position
        self._second_sc = self.style().hitTestComplexControl(
            QStyle.CC_Slider, self.opt, event.pos(), self
        )

    def mouseMoveEvent(self, event: QMouseEvent):
        if not event.buttons() & Qt.LeftButton:
            return

        event.accept()

        # Calculate slider value based on mouse position
        pos = self.pixelPosToRangeValue(event.pos())

        if self._first_sc == QStyle.SC_SliderHandle:
            if pos <= self.second_position:
                self.first_position = pos
                self.update()
                self.valueChanged.emit()
        elif self._second_sc == QStyle.SC_SliderHandle:
            if pos >= self.first_position:
                self.second_position = pos
                self.update()
                self.valueChanged.emit()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._first_sc = None
        self._second_sc = None

    def pixelPosToRangeValue(self, pos):
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)

        groove = self.style().subControlRect(
            QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self
        )
        handle = self.style().subControlRect(
            QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self
        )

        if self.orientation() == Qt.Horizontal:
            sliderLength = handle.width()
            sliderMin = groove.x()
            sliderMax = groove.right() - sliderLength + 1
            pos = pos.x()
        else:
            sliderLength = handle.height()
            sliderMin = groove.y()
            sliderMax = groove.bottom() - sliderLength + 1
            pos = pos.y()

        return QStyle.sliderValueFromPosition(
            self.opt.minimum,
            self.opt.maximum,
            pos - sliderMin,
            sliderMax - sliderMin,
            opt.upsideDown,
        )

    def initStyleOption(self, option):
        option.initFrom(self)
        option.minimum = self.opt.minimum
        option.maximum = self.opt.maximum
        option.tickPosition = self.opt.tickPosition
        option.tickInterval = self.opt.tickInterval
        option.upsideDown = self.orientation() == Qt.Vertical
        option.subControls = QStyle.SC_SliderGroove | QStyle.SC_SliderHandle
        option.activeSubControls = QStyle.SC_None

    def orientation(self):
        return Qt.Horizontal

    def sizeHint(self):
        """override"""
        SliderLength = 84
        TickSpace = 5

        w = SliderLength
        h = self.style().pixelMetric(QStyle.PM_SliderThickness, self.opt, self)

        if (
            self.opt.tickPosition & QSlider.TicksAbove
            or self.opt.tickPosition & QSlider.TicksBelow
        ):
            h += TickSpace

        return (
            self.style()
            .sizeFromContents(QStyle.CT_Slider, self.opt, QSize(w, h), self)
            .expandedTo(QApplication.globalStrut())
        )

def add_range_sliders(widget, bounds):
    # Create a horizontal layout for the sliders
    slider_layout = QHBoxLayout()

    # X-axis slider
    widget.x_slider = RangeSlider()
    widget.x_slider.setRangeLimit(int(bounds[0]), int(bounds[1]))
    widget.x_slider.setRange(int(bounds[0]), int(bounds[1]))
    slider_layout.addWidget(QLabel("X Range"))
    slider_layout.addWidget(widget.x_slider)

    # Y-axis slider
    widget.y_slider = RangeSlider()
    widget.y_slider.setRangeLimit(int(bounds[2]), int(bounds[3]))
    widget.y_slider.setRange(int(bounds[2]), int(bounds[3]))
    slider_layout.addWidget(QLabel("Y Range"))
    slider_layout.addWidget(widget.y_slider)

    # Z-axis slider
    widget.z_slider = RangeSlider()
    widget.z_slider.setRangeLimit(int(bounds[4]), int(bounds[5]))
    widget.z_slider.setRange(int(bounds[4]), int(bounds[5]))
    slider_layout.addWidget(QLabel("Z Range"))
    slider_layout.addWidget(widget.z_slider)

    # Connect slider value changes to the update_function method
    widget.x_slider.valueChanged.connect(widget.update_function)
    widget.y_slider.valueChanged.connect(widget.update_function)
    widget.z_slider.valueChanged.connect(widget.update_function)

    widget.layout.addLayout(slider_layout)