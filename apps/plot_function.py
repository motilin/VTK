import os
import sys
from src.core.constants import WINDOW_WIDTH, WINDOW_HEIGHT

# Dynamically set PYTHONPATH in .env
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.environ["PYTHONPATH"] = project_root
sys.path.append(project_root)

from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QWidget,
    QPushButton,
    QSlider,
)
from PyQt5.QtCore import Qt, QEvent, QRect, QSize
from PyQt5.QtGui import QPainter, QBrush, QPalette, QPaintEvent, QMouseEvent
from PyQt5.QtWidgets import QStyle, QStyleOptionSlider
import vtk
from qt.main_window import VTKMainWindow
from qt.callbacks import toggle_visibility
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from src.core.visualization import configure_window, set_mathematical_view
from src.core.constants import WINDOW_WIDTH, WINDOW_HEIGHT, colors
from src.utils.surface_utils import (
    create_implicit_surface_actor,
    set_z_gradient_coloring,
)
from src.utils.line_utils import create_axes
from qt.vtk_widget import VTKWidget
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


class PlotFunc(VTKWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.renderer.SetBackground(colors.GetColor3d("dark_blue"))

        # Add axes
        self.math_axes = create_axes(length=10)
        self.renderer.AddActor(self.math_axes)

        # Initialize bounds
        self.x_min, self.x_max = -10, 10
        self.y_min, self.y_max = -10, 10
        self.z_min, self.z_max = -10, 10

        # Create sliders
        self.create_sliders()

        # Add function
        self.update_function()

        # Create a toggle button for axes visibility
        self.toggle_button = QPushButton("Toggle Axes Visibility", self)
        self.toggle_button.clicked.connect(
            lambda: toggle_visibility(self.vtk_widget, self.math_axes)
        )
        self.layout.addWidget(self.toggle_button)

        # Initialize the interactor
        set_mathematical_view(self.renderer)
        self.vtk_widget.GetRenderWindow().Render()
        self.interactor.Initialize()

    def create_sliders(self):
        # Create a horizontal layout for the sliders
        slider_layout = QHBoxLayout()

        # X-axis slider
        self.x_slider = RangeSlider()
        self.x_slider.setRangeLimit(int(self.x_min * 10), int(self.x_max * 10))
        self.x_slider.setRange(int(self.x_min * 10), int(self.x_max * 10))
        slider_layout.addWidget(QLabel("X Range"))
        slider_layout.addWidget(self.x_slider)

        # Y-axis slider
        self.y_slider = RangeSlider()
        self.y_slider.setRangeLimit(int(self.y_min * 10), int(self.y_max * 10))
        self.y_slider.setRange(int(self.y_min * 10), int(self.y_max * 10))
        slider_layout.addWidget(QLabel("Y Range"))
        slider_layout.addWidget(self.y_slider)

        # Z-axis slider
        self.z_slider = RangeSlider()
        self.z_slider.setRangeLimit(int(self.z_min * 10), int(self.z_max * 10))
        self.z_slider.setRange(int(self.z_min * 10), int(self.z_max * 10))
        slider_layout.addWidget(QLabel("Z Range"))
        slider_layout.addWidget(self.z_slider)

        # Connect slider value changes to the update_function method
        self.x_slider.valueChanged.connect(self.update_function)
        self.y_slider.valueChanged.connect(self.update_function)
        self.z_slider.valueChanged.connect(self.update_function)

        self.layout.addLayout(slider_layout)

    def update_function(self):
        self.x_min, self.x_max = self.x_slider.getRange()
        self.x_min /= 10
        self.x_max /= 10
        self.y_min, self.y_max = self.y_slider.getRange()
        self.y_min /= 10
        self.y_max /= 10
        self.z_min, self.z_max = self.z_slider.getRange()
        self.z_min /= 10
        self.z_max /= 10

        def implicit_equation(x, y, z):
            return x**2 + y**2 - z**2 - 1

        surface_actor = self.get_surface_actor(
            implicit_equation,
            (self.x_min, self.x_max, self.y_min, self.y_max, self.z_min, self.z_max),
        )
        self.renderer.RemoveAllViewProps()
        self.renderer.AddActor(self.math_axes)
        self.renderer.AddActor(surface_actor)
        self.vtk_widget.GetRenderWindow().Render()

    def get_surface_actor(self, implicit_function, bounds):
        surface_actor = create_implicit_surface_actor(implicit_function, bounds)
        set_z_gradient_coloring(
            surface_actor, colors.GetColor3d("emerald"), colors.GetColor3d("coral")
        )
        return surface_actor


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VTKMainWindow(PlotFunc())
    window.setWindowTitle("Interactive Function Plotter")
    window.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
    window.show()
    sys.exit(app.exec_())
