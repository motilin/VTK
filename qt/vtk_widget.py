from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton

import vtk
from qt.callbacks import toggle_visibility
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from src.core.visualization import configure_window, set_mathematical_view
from src.core.constants import WINDOW_WIDTH, WINDOW_HEIGHT, colors
from src.core import CustomInteractorStyle
from src.utils.surface_utils import (
    create_implicit_surface_actor,
    set_z_gradient_coloring,
)
from src.utils.line_utils import create_axes


class VTKWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set up the main layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Create the VTK render window interactor
        self.vtk_widget = QVTKRenderWindowInteractor(self)
        self.layout.addWidget(self.vtk_widget)

        # Set up the VTK renderer and window
        self.renderer = vtk.vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        self.interactor = self.vtk_widget.GetRenderWindow().GetInteractor()

        # Set up interactor style
        style = CustomInteractorStyle()
        self.interactor.SetInteractorStyle(style)
