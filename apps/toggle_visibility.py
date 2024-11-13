import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class VTKWidget(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main widget and layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Create the VTK render window interactor
        self.vtk_widget = QVTKRenderWindowInteractor(self.central_widget)
        self.layout.addWidget(self.vtk_widget)

        # Create the button
        self.toggle_button = QPushButton("Toggle Shape Visibility", self)
        self.toggle_button.clicked.connect(self.toggle_visibility)
        self.layout.addWidget(self.toggle_button)

        # Set up the VTK renderer and window
        self.renderer = vtk.vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        self.interactor = self.vtk_widget.GetRenderWindow().GetInteractor()

        # Create a simple VTK shape (e.g., a cube)
        self.cube = vtk.vtkCubeSource()
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputConnection(self.cube.GetOutputPort())
        self.actor = vtk.vtkActor()
        self.actor.SetMapper(self.mapper)

        # Add the actor to the renderer
        self.renderer.AddActor(self.actor)
        self.renderer.SetBackground(0.1, 0.2, 0.4)  # Set a background color

        # Initialize visibility state
        self.shape_visible = True

        # Initialize the interactor
        self.vtk_widget.GetRenderWindow().Render()
        self.interactor.Initialize()

    def toggle_visibility(self):
        # Toggle the visibility of the actor
        self.shape_visible = not self.shape_visible
        self.actor.SetVisibility(self.shape_visible)
        self.vtk_widget.GetRenderWindow().Render()


# Run the application
app = QApplication(sys.argv)
window = VTKWidget()
window.setWindowTitle("VTK Shape in Qt with Visibility Toggle")
window.show()
sys.exit(app.exec_())
