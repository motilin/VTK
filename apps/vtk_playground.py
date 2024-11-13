import vtk
import sys
from sympy import symbols, pi, Eq, pretty, latex
from sympy.parsing.sympy_parser import parse_expr
from rich import print

# Create a cylinder using VTK
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersSources import vtkCylinderSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkTextActor,
    vtkTextProperty,
)
from vtkmodules.vtkInteractionWidgets import (
    vtkSliderRepresentation2D,
    vtkSliderWidget,
)


###############
## Constants ##
###############


WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 1200
SLIDER_START_X = 80
SLIDER_WIDTH = 200
SLIDER_HEIGHT = 40


## Define named colors objects

colors = vtkNamedColors()
dark_blue = map(lambda x: x / 255.0, [26, 51, 102, 255])
colors.SetColor("dark_blue", *dark_blue)


###########################
## Functions and classes ##
###########################


# Custom interactor style to handle key press events
class CustomInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, parent=None):
        self.AddObserver("KeyPressEvent", self.on_key_press_event)

    def on_key_press_event(self, obj, event):
        key = self.GetInteractor().GetKeySym()
        if key == "q":
            self.GetInteractor().GetRenderWindow().Finalize()
            self.GetInteractor().TerminateApp()
            sys.exit(0)  # Gracefully exit the application


# Function to create a custom slider widget
def create_custom_slider_widget(
    iren, slider_index, min_val, max_val, init_val, callback, title
):
    height = WINDOW_HEIGHT - SLIDER_HEIGHT * slider_index
    slider_rep = vtkSliderRepresentation2D()
    slider_rep.SetMinimumValue(min_val)
    slider_rep.SetMaximumValue(max_val)
    slider_rep.SetValue(init_val)
    slider_rep.GetPoint1Coordinate().SetCoordinateSystemToDisplay()
    slider_rep.GetPoint1Coordinate().SetValue(SLIDER_START_X, height)
    slider_rep.GetPoint2Coordinate().SetCoordinateSystemToDisplay()
    slider_rep.GetPoint2Coordinate().SetValue(SLIDER_START_X + SLIDER_WIDTH, height)
    slider_rep.SetSliderLength(0.0001)
    slider_rep.SetSliderWidth(0.02)
    slider_rep.SetEndCapLength(0.01)
    slider_rep.SetEndCapWidth(0.03)
    slider_rep.SetTubeWidth(0.005)  # Set the tube width
    slider_rep.GetTubeProperty().SetColor(colors.GetColor3d("Gray"))
    slider_rep.ShowSliderLabelOff()  # Disable the default slider value label

    # Create the slider widget
    slider_widget = vtkSliderWidget()
    slider_widget.SetInteractor(iren)
    slider_widget.SetRepresentation(slider_rep)
    slider_widget.AddObserver("InteractionEvent", callback)
    slider_widget.EnabledOn()

    # Create custom text actor for slider title
    title_text = vtkTextActor()
    title_text.SetInput(title)
    title_text.GetTextProperty().SetFontSize(16)
    title_text.GetTextProperty().SetColor(colors.GetColor3d("White"))
    title_text.SetPosition(SLIDER_START_X + SLIDER_WIDTH + 10, height - 10)
    ren.AddActor(title_text)

    # Create custom text actor for slider value
    value_text = vtkTextActor()
    value_text.SetInput(f"{init_val:.2f}")
    value_text.GetTextProperty().SetFontSize(16)
    value_text.GetTextProperty().SetColor(colors.GetColor3d("White"))
    value_text.SetPosition(SLIDER_START_X - 50, height - 10)
    ren.AddActor(value_text)

    return slider_widget, value_text


########################
## Callback functions ##
########################


# Slider callback function to change the cylinder's color
def color_slider_callback(obj, event):
    slider_rep = obj.GetRepresentation()
    value = slider_rep.GetValue()
    cylinderActor.GetProperty().SetColor(value, 0.0, 1.0 - value)
    color_value_text.SetInput(f"{value:.2f}")
    color_value_text.Modified()
    renWin.Render()


# Slider callback function to change the cylinder's resolution
def resolution_slider_callback(obj, event):
    slider_rep = obj.GetRepresentation()
    value = int(slider_rep.GetValue())
    cylinder.SetResolution(value)
    cylinderMapper.SetInputConnection(cylinder.GetOutputPort())
    resolution_value_text.SetInput(str(value))
    resolution_value_text.Modified()
    renWin.Render()


# Slider callback function to change the cylinder's height/width ratio
def ratio_slider_callback(obj, event):
    slider_rep = obj.GetRepresentation()
    value = slider_rep.GetValue()
    cylinder.SetHeight(value)
    cylinderMapper.SetInputConnection(cylinder.GetOutputPort())
    ratio_value_text.SetInput(f"{value:.2f}")
    ratio_value_text.Modified()
    renWin.Render()


###############################################
## Setup the rendering window and interactor ##
###############################################


# Create the graphics structure. The renderer renders into the render window.
ren = vtkRenderer()
renWin = vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# Set the custom interactor style for handling key press events
style = CustomInteractorStyle()
iren.SetInteractorStyle(style)

# Set the background and size
ren.SetBackground(colors.GetColor3d("dark_blue"))
renWin.SetSize(WINDOW_WIDTH, WINDOW_HEIGHT)  # Set the render window size
renWin.SetWindowName("Cylinder Example")  # Set the window title


########################################
############ Create objects ############
########################################

a = 2
b = 3
c = 4
x, y, z = symbols("x y z")
# Define an implicit equation
eq = Eq(a * x**2 + b * y**2 + c * z**2, 1)
print(pretty(eq))

#### An example shape. Replace with the appropriate quadratic surface

# Create a polygonal cylinder model with eight circumferential facets.
cylinder = vtkCylinderSource()
cylinder.SetResolution(8)

# The mapper is responsible for pushing the geometry into the graphics library.
cylinderMapper = vtkPolyDataMapper()
cylinderMapper.SetInputConnection(cylinder.GetOutputPort())

# The actor is a grouping mechanism: besides the geometry (mapper), it also has a property, transformation matrix, and/or texture map.
cylinderActor = vtkActor()
cylinderActor.SetMapper(cylinderMapper)
cylinderActor.GetProperty().SetColor(colors.GetColor3d("Tomato"))
cylinderActor.RotateX(30.0)
cylinderActor.RotateY(-45.0)
ren.AddActor(cylinderActor)


########################################
## Create custom slider widgets ########
########################################


color_slider, color_value_text = create_custom_slider_widget(
    iren, 1, 0.0, 1.0, 0.5, color_slider_callback, "Color"
)

# Create the resolution slider widget
resolution_slider, resolution_value_text = create_custom_slider_widget(
    iren, 2, 3, 50, 8, resolution_slider_callback, "Resolution"
)

# Create the ratio slider widget
ratio_slider, ratio_value_text = create_custom_slider_widget(
    iren,
    3,
    0.1,
    5.0,
    1.0,
    ratio_slider_callback,
    "Height/Width Ratio",
)


################################################
## Set up the camera and start the event loop ##
################################################


iren.Initialize()  # Initialize the event handler
ren.ResetCamera()
ren.GetActiveCamera().Zoom(1.5)  # Zoom in by a factor of 1.5
renWin.Render()
iren.Start()  # Start the event loop.
