"""
Example implementation showing how to use the quadratic surface visualization framework.
"""

from sympy import symbols, pi, Eq
from src.core.visualization import setup_renderer, configure_window
from src.core.constants import WINDOW_WIDTH, WINDOW_HEIGHT
from src.core.interactor import CustomInteractorStyle
from src.widgets.sliders import SliderManager
from src.widgets.callbacks import SliderCallbacks
from vtkmodules.vtkFiltersSources import vtkCylinderSource
from vtkmodules.vtkRenderingCore import vtkPolyDataMapper, vtkActor
from vtkmodules.vtkCommonColor import vtkNamedColors  # Import vtkNamedColors


def main():
    # Setup
    ren, renWin, iren = setup_renderer()
    configure_window(renWin, ren, WINDOW_WIDTH, WINDOW_HEIGHT, "Cylinder Example")

    # Set up interactor style
    style = CustomInteractorStyle()
    iren.SetInteractorStyle(style)

    # Create cylinder
    cylinder = vtkCylinderSource()
    cylinder.SetResolution(8)

    # Create mapper and actor
    cylinderMapper = vtkPolyDataMapper()
    cylinderMapper.SetInputConnection(cylinder.GetOutputPort())

    cylinderActor = vtkActor()
    cylinderActor.SetMapper(cylinderMapper)

    colors = vtkNamedColors()  # Define colors
    cylinderActor.GetProperty().SetColor(colors.GetColor3d("Tomato"))
    cylinderActor.RotateX(30.0)
    cylinderActor.RotateY(-45.0)

    ren.AddActor(cylinderActor)

    # Initialize slider managers
    slider_manager = SliderManager(ren, iren)
    callbacks = SliderCallbacks(renWin)

    # Register actors and create callbacks
    callbacks.register_actor("cylinder", cylinderActor)

    # Create sliders with callbacks
    color_slider, color_text = slider_manager.create_slider(
        "color", 1, 0.0, 1.0, 0.5, callbacks.create_color_callback(), "Color"
    )
    callbacks.register_value_text("color", color_text)

    resolution_slider, resolution_text = slider_manager.create_slider(
        "resolution",
        2,
        3,
        50,
        8,
        callbacks.create_resolution_callback(cylinder),
        "Resolution",
    )
    callbacks.register_value_text("resolution", resolution_text)

    ratio_slider, ratio_text = slider_manager.create_slider(
        "ratio",
        3,
        0.1,
        5.0,
        1.0,
        callbacks.create_ratio_callback(cylinder),
        "Height/Width Ratio",
    )
    callbacks.register_value_text("ratio", ratio_text)

    # Initialize and start
    iren.Initialize()
    ren.ResetCamera()
    ren.GetActiveCamera().Zoom(1.5)
    renWin.Render()
    iren.Start()


if __name__ == "__main__":
    main()
