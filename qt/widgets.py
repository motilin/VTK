from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QSizePolicy,
    QLabel,
    QComboBox,
    QHBoxLayout,
    QSlider,
)
from PyQt5.QtCore import Qt
import vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from src.core.interactor import CustomInteractorStyle
from qt.range_slider import RangeSlider, add_range_sliders
from src.core.constants import CONTROL_PANEL_WIDTH, CONTROL_PANEL_SPACING


class VTKWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.vtk_widget = QVTKRenderWindowInteractor(self)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.vtk_widget)
        self.setLayout(self.layout)

        self.renderer = vtk.vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        self.interactor = self.vtk_widget.GetRenderWindow().GetInteractor()

        style = CustomInteractorStyle()
        self.interactor.SetInteractorStyle(style)

    def get_render_window(self):
        return self.vtk_widget.GetRenderWindow()


class ControlWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.layout.setSpacing(CONTROL_PANEL_SPACING)
        self.layout.setAlignment(Qt.AlignTop | Qt.AlignRight)
        self.setLayout(self.layout)
        self.setFixedWidth(CONTROL_PANEL_WIDTH)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

    def add_slider(self, bounds, text, update_callback):
        label = QLabel(text, self)
        label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Prevent label from expanding
        
        SCALE_FACTOR = 100  # For 0.01 precision
        
        slider = QSlider(Qt.Horizontal, self)
        slider.setMinimum(int(bounds[0] * SCALE_FACTOR))
        slider.setMaximum(int(bounds[1] * SCALE_FACTOR))
        
        def scaled_callback(value):
            # Convert the integer value back to float with 0.01 precision
            scaled_value = value / SCALE_FACTOR
            update_callback(scaled_value)
            
        slider.valueChanged.connect(scaled_callback)
        slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Make slider expand horizontally
        
        slider_layout = QHBoxLayout()
        slider_layout.setSpacing(5)  # Small spacing between label and slider
        slider_layout.addWidget(label)  # Remove alignment to let it take minimum space
        slider_layout.addWidget(slider, stretch=1)  # Add stretch factor to make slider expand
        slider_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
    
        self.layout.addLayout(slider_layout)

    def add_range_sliders(self, bounds, update_callback):
        add_range_sliders(
            self,
            bounds,
            self.layout,
            update_callback,
        )

    def add_button(self, text, callback):
        button = QPushButton(text, self)
        button.clicked.connect(callback)
        button_layout = QHBoxLayout()
        button_layout.addWidget(button, alignment=Qt.AlignTop)
        self.layout.addLayout(button_layout)

    def add_dropdown(self, text, options, callback):
        label = QLabel(text, self)
        dropdown = QComboBox(self)
        dropdown.addItems(options)
        dropdown.currentIndexChanged.connect(callback)
        dropdown_layout = QHBoxLayout()
        dropdown_layout.addWidget(label, alignment=Qt.AlignLeft)
        dropdown_layout.addWidget(dropdown, alignment=Qt.AlignLeft)
        self.layout.addLayout(dropdown_layout)