from PyQt5.QtWidgets import QWidget, QVBoxLayout, QWidget
import vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from src.core.interactor import CustomInteractorStyle

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
        
    def GetRenderWindow(self):
        return self.vtk_widget.GetRenderWindow()