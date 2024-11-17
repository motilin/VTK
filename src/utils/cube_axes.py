import vtk
from vtkmodules.vtkFiltersSources import vtkSuperquadricSource
from vtkmodules.vtkRenderingAnnotation import vtkCubeAxesActor
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
)
from src.core.constants import COLORS, X_MIN, X_MAX, Y_MIN, Y_MAX, Z_MIN, Z_MAX


def create_cube_axes_actor(bounds, renderer):
    """
    Creates a cube axes actor with proper color handling.

    Args:
        bounds (tuple): (x_min, x_max, y_min, y_max, z_min, z_max)
        renderer: vtkRenderer object

    Returns:
        vtkCubeAxesActor: Cube axes
    """
    # Validate bounds
    if len(bounds) != 6:
        raise ValueError(
            "Bounds must be a tuple of 6 values: (x_min, x_max, y_min, y_max, z_min, z_max)"
        )

    x_min, x_max, y_min, y_max, z_min, z_max = bounds

    # Define colors
    actorColor = COLORS.GetColor3d("Tomato")
    axis1Color = COLORS.GetColor3d("Salmon")
    axis2Color = COLORS.GetColor3d("PaleGreen")
    axis3Color = COLORS.GetColor3d("LightSkyBlue")

    # Create a superquadric
    superquadricSource = vtkSuperquadricSource()
    superquadricSource.SetPhiRoundness(3.1)
    superquadricSource.SetThetaRoundness(1.0)
    superquadricSource.Update()

    # Set up the superquadric actor
    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(superquadricSource.GetOutputPort())
    superquadricActor = vtkActor()
    superquadricActor.SetMapper(mapper)
    superquadricActor.GetProperty().SetDiffuseColor(actorColor)
    superquadricActor.GetProperty().SetDiffuse(0.7)
    superquadricActor.GetProperty().SetSpecular(0.7)
    superquadricActor.GetProperty().SetSpecularPower(50.0)

    # Create and configure the cube axes actor
    cubeAxesActor = vtkCubeAxesActor()
    cubeAxesActor.SetUseTextActor3D(True)

    # Set the bounds directly from the input parameters
    cubeAxesActor.SetBounds(x_min, x_max, y_min, y_max, z_min, z_max)

    cubeAxesActor.SetCamera(renderer.GetActiveCamera())

    # Configure axis properties
    for i, color in enumerate([axis1Color, axis2Color, axis3Color]):
        cubeAxesActor.GetTitleTextProperty(i).SetColor(color)
        cubeAxesActor.GetLabelTextProperty(i).SetColor(color)
        if i == 0:  # Only set font size for X axis
            cubeAxesActor.GetTitleTextProperty(i).SetFontSize(48)

    # Configure gridlines
    cubeAxesActor.DrawXGridlinesOn()
    cubeAxesActor.DrawYGridlinesOn()
    cubeAxesActor.DrawZGridlinesOn()
    cubeAxesActor.SetGridLineLocation(cubeAxesActor.VTK_GRID_LINES_FURTHEST)

    # Configure ticks
    cubeAxesActor.XAxisMinorTickVisibilityOff()
    cubeAxesActor.YAxisMinorTickVisibilityOff()
    cubeAxesActor.ZAxisMinorTickVisibilityOff()

    cubeAxesActor.SetFlyModeToStaticEdges()
    
    return cubeAxesActor
