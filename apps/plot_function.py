import os
import sys

# Dynamically set PYTHONPATH in .env
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.environ["PYTHONPATH"] = project_root
sys.path.append(project_root)

from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QPushButton,
    QSlider,
)
from PyQt5.QtCore import Qt, QRect, QSize
from PyQt5.QtWidgets import QStyle, QStyleOptionSlider
import vtk
from qt.main_window import VTKMainWindow
from qt.callbacks import toggle_visibility
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from src.core.visualization import set_mathematical_view
from src.core.constants import WINDOW_WIDTH, WINDOW_HEIGHT, colors
from src.utils.surface_utils import (
    create_implicit_surface_actor,
    set_z_gradient_coloring,
)
from src.utils.line_utils import create_axes
from qt.vtk_widget import VTKWidget
from qt.sliders import RangeSlider


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
