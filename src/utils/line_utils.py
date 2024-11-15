import vtk
import numpy as np
from src.core.constants import AXES_LENGTH, COLORS
import vtk.numpy_interface.dataset_adapter as dsa  # type: ignore
import vtk.util.numpy_support as numpy_support  # type: ignore


def create_axes(length=AXES_LENGTH, line_width=0.5, font_size=24, cone_radius=0.2):
    """
    Creates coordinate axes with larger labels and smaller arrow heads
    Parameters:
    -----------
    length : float
        Size of the axes
    line_width : float
        Width of the axis lines
    font_size : int
        Size of the X,Y,Z labels
    cone_radius : float
        Size of the arrow heads relative to default
    Returns:
    --------
    vtk.vtkAxesActor
        The customized axes actor
    """
    axes = vtk.vtkAxesActor()
    # Set the axes length
    axes.SetTotalLength(length, length, length)
    # Set line width
    axes.GetXAxisShaftProperty().SetLineWidth(line_width)
    axes.GetYAxisShaftProperty().SetLineWidth(line_width)
    axes.GetZAxisShaftProperty().SetLineWidth(line_width)
    # Customize labels
    axes.SetXAxisLabelText("x")
    axes.SetYAxisLabelText("y")
    axes.SetZAxisLabelText("z")

    # Create custom text properties for each axis caption
    for caption_actor in [
        axes.GetXAxisCaptionActor2D(),
        axes.GetYAxisCaptionActor2D(),
        axes.GetZAxisCaptionActor2D(),
    ]:
        # Enable caption scaling
        caption_actor.SetCaption("")  # Clear default caption
        caption_actor.BorderOff()
        caption_actor.LeaderOff()

        # Get the text property
        text_property = caption_actor.GetCaptionTextProperty()

        # Set text properties
        text_property.SetFontFamily(vtk.VTK_FONT_FILE)
        text_property.SetFontSize(font_size)
        text_property.SetBold(True)
        text_property.SetShadow(False)

        # Set the position and height of the caption
        caption_actor.SetAttachmentPoint(
            length, 0, 0
        )  # This will be different for each axis
        caption_actor.SetPosition(
            length + 0.2 * length, 0
        )  # Adjust position relative to axis end

        # Enable non-scaled text
        caption_actor.GetTextActor().SetTextScaleModeToNone()

    # Adjust individual axis caption positions
    axes.GetYAxisCaptionActor2D().SetAttachmentPoint(0, length, 0)
    axes.GetYAxisCaptionActor2D().SetAttachmentPoint(0, length + 0.2 * length, 0)

    axes.GetZAxisCaptionActor2D().SetAttachmentPoint(0, 0, length)
    axes.GetZAxisCaptionActor2D().SetAttachmentPoint(0, 0, length + 0.2 * length)

    # Customize arrow heads
    axes.SetConeRadius(cone_radius)
    axes.SetConeResolution(16)  # Smooth cone
    axes.SetShaftTypeToCylinder()
    axes.SetCylinderRadius(cone_radius * 0.05)  # Decrease cylinder radius
    axes.SetNormalizedShaftLength(0.85, 0.85, 0.85)  # Adjust shaft length
    axes.SetNormalizedTipLength(0.15, 0.15, 0.15)  # Adjust tip length

    return axes


def create_plane_points(bounds, k, is_x_plane, resolution):
    """
    Creates points for a vertical plane at x=k or y=k using vectorized operations.

    Parameters:
    -----------
    bounds : tuple
        The bounds of the function (xmin, xmax, ymin, ymax, zmin, zmax)
    k : float
        The position of the plane
    is_x_plane : bool
        True if creating points for x=k plane, False for y=k plane
    resolution : int
        Number of points along each dimension

    Returns:
        numpy array of points
    """
    if is_x_plane:
        y = np.linspace(bounds[2], bounds[3], resolution)
        z = np.linspace(bounds[4], bounds[5], resolution)
        Y, Z = np.meshgrid(y, z, indexing="ij")
        X = np.full_like(Y, k)
    else:
        x = np.linspace(bounds[0], bounds[1], resolution)
        z = np.linspace(bounds[4], bounds[5], resolution)
        X, Z = np.meshgrid(x, z, indexing="ij")
        Y = np.full_like(X, k)

    return np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1)


def evaluate_function_on_points(points, implicit_func):
    """
    Vectorized evaluation of the implicit function on given points.

    Parameters:
    -----------
    points : numpy array
        Array of 3D points
    implicit_func : callable
        Function that accepts arrays x, y, z

    Returns:
        numpy array of function values
    """
    return implicit_func(points[:, 0], points[:, 1], points[:, 2])


def create_contour_polydata(points, values, resolution):
    """
    Creates VTK polydata for contour lines using structured grid.

    Parameters:
    -----------
    points : numpy array
        Array of 3D points
    values : numpy array
        Function values at points
    resolution : int
        Grid resolution

    Returns:
        vtkPolyData object
    """
    # Create structured grid
    grid = vtk.vtkStructuredGrid()
    grid.SetDimensions(resolution, resolution, 1)  # 2D grid

    # Set the points
    vtk_points = vtk.vtkPoints()
    vtk_points.SetData(numpy_support.numpy_to_vtk(points, deep=True))
    grid.SetPoints(vtk_points)

    # Set the scalar values
    vtk_scalars = numpy_support.numpy_to_vtk(values, deep=True)
    vtk_scalars.SetName("values")
    grid.GetPointData().SetScalars(vtk_scalars)

    # Create and update contour filter
    contour = vtk.vtkContourFilter()
    contour.SetInputData(grid)
    contour.SetValue(0, 0.0)
    contour.Update()

    return contour.GetOutput()


def create_func_traces_actor(
    implicit_func, bounds, space=1, thickness=2, color=COLORS.GetColor3d('charcoal'), resolution=50
):
    """
    Creates an implicit function traces actor with proper transparency handling.
    
    Parameters:
    -----------
    implicit_func : callable
        Vectorized function that takes x, y, z arrays and returns function values
    bounds : tuple
        The bounds of the function (xmin, xmax, ymin, ymax, zmin, zmax)
    space : float
        The space between the traces
    transparency : float
        Transparency of the traces (0 = fully opaque, 1 = fully transparent)
    thickness : int
        Thickness of the traces
    color : tuple
        RGB values (0-1) for the traces
    resolution : int
        The resolution of the traces
    
    Returns:
        vtkActor object
    """
    # Create append filter to combine all contours
    append_filter = vtk.vtkAppendPolyData()
    
    # Create x-plane contours using vectorized operations
    x_values = np.arange(bounds[0], bounds[1] + space, space)
    for x in x_values:
        points = create_plane_points(bounds, x, True, resolution)
        values = evaluate_function_on_points(points, implicit_func)
        contour_data = create_contour_polydata(points, values, resolution)
        append_filter.AddInputData(contour_data)
    
    # Create y-plane contours using vectorized operations
    y_values = np.arange(bounds[2], bounds[3] + space, space)
    for y in y_values:
        points = create_plane_points(bounds, y, False, resolution)
        values = evaluate_function_on_points(points, implicit_func)
        contour_data = create_contour_polydata(points, values, resolution)
        append_filter.AddInputData(contour_data)
    
    append_filter.Update()
    
    # Create optimized visualization pipeline
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(append_filter.GetOutputPort())
    mapper.ScalarVisibilityOff()
    
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    
    # Set up properties for transparency and appearance
    properties = actor.GetProperty()
    properties.SetColor(color)
    properties.SetLineWidth(thickness)
    
    # Enable line transparency
    properties.SetRepresentationToWireframe()
    properties.LightingOff()  # Disable lighting effects on lines
    properties.SetAmbient(1.0)  # Full ambient lighting for consistent line appearance
    properties.SetDiffuse(0.0)  # No diffuse lighting
    properties.SetSpecular(0.0)  # No specular lighting
    
    # Enable rendering lines as tubes for improved appearance
    properties.SetRenderLinesAsTubes(True)
    
    return actor
