import vtk
import numpy as np
from src.core.constants import (
    AXES_LENGTH,
    COLORS,
    X_MIN,
    X_MAX,
    Y_MIN,
    Y_MAX,
    Z_MIN,
    Z_MAX,
)
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
    try:
        values = implicit_func(points[:, 0], points[:, 1], points[:, 2])
        return values
    except Exception as e:
        print(f"Error: {e}")
        return np.ones(len(points))


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

    if points.size < grid.GetNumberOfPoints() or values.size < grid.GetNumberOfPoints():
        print("Error: Insufficient points or values")
        return None

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
    implicit_func,
    bounds,
    space=1,
    thickness=2,
    color=COLORS.GetColor3d("charcoal"),
    opacity=1.0,
    resolution=50,
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
    if space == 0 or thickness == 0 or opacity == 0:
        return None
    space = abs(space)

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
    properties.SetOpacity(opacity)

    # Enable rendering lines as tubes for improved appearance
    properties.SetRenderLinesAsTubes(True)

    return actor


def create_parametric_curve_actor(
    parametric_func,  # NumPy function (t) -> (x,y,z)
    t_range=(0, 1),  # t range
    color=COLORS.GetColor3d("charcoal"),  # Actor color
    thickness=1.0,  # Tube thickness
    opacity=1.0,  # Actor opacity
    dash_spacing=0.0,  # Dash spacing (0 = solid line)
    global_bounds=(X_MIN, X_MAX, Y_MIN, Y_MAX, Z_MIN, Z_MAX),
):
    if thickness == 0 or opacity == 0:
        return None

    # Dynamic resolution calculation
    t_span = abs(t_range[1] - t_range[0])
    tube_radius = thickness / 40

    # Resolution facor
    base_resolution = int(max(200, min(100, t_span * 200)))
    thickness_factor = max(1, 20 * tube_radius)
    curvature_resolution = int(base_resolution * thickness_factor)

    # Bound the resolution to prevent extreme values
    resolution = max(50, min(curvature_resolution, 1000))

    # Generate points
    t_min, t_max = t_range
    t_values = np.linspace(t_min, t_max, resolution)

    # Unpack bounds
    x_min, x_max, y_min, y_max, z_min, z_max = global_bounds

    def is_within_bounds(x, y, z):
        return x_min <= x <= x_max and y_min <= y <= y_max and z_min <= z <= z_max

    # Create points and cells for the complete curve
    points = vtk.vtkPoints()
    lines = vtk.vtkCellArray()

    if dash_spacing > 0:
        # Invert dash spacing logic: larger value = larger gaps
        base_dash_points = int(max(3, resolution / 20))  # minimum dash size
        space_points = int(
            base_dash_points * dash_spacing
        )  # space grows with dash_spacing
        dash_points = base_dash_points  # keep dash size constant

        # Create dashed line segments
        current_point = 0
        while current_point < resolution:
            # Add a dash segment
            if current_point + dash_points <= resolution:
                # Collect points for this dash segment
                dash_point_ids = []
                for i in range(dash_points):
                    idx = current_point + i
                    x, y, z = parametric_func(t_values[idx])
                    if is_within_bounds(x, y, z):
                        point_id = points.InsertNextPoint(x, y, z)
                        dash_point_ids.append(point_id)

                # Only create line segment if we have at least 2 valid points
                if len(dash_point_ids) >= 2:
                    line = vtk.vtkPolyLine()
                    line.GetPointIds().SetNumberOfIds(len(dash_point_ids))
                    for i, point_id in enumerate(dash_point_ids):
                        line.GetPointIds().SetId(i, point_id)
                    lines.InsertNextCell(line)

                current_point += dash_points + space_points
            else:
                break
    else:
        # Create continuous line, collecting only valid points
        valid_point_ids = []
        for i in range(resolution):
            x, y, z = parametric_func(t_values[i])
            if is_within_bounds(x, y, z):
                point_id = points.InsertNextPoint(x, y, z)
                valid_point_ids.append(point_id)

        # Only create line if we have at least 2 valid points
        if len(valid_point_ids) >= 2:
            line = vtk.vtkPolyLine()
            line.GetPointIds().SetNumberOfIds(len(valid_point_ids))
            for i, point_id in enumerate(valid_point_ids):
                line.GetPointIds().SetId(i, point_id)
            lines.InsertNextCell(line)

    # Create polydata
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    polydata.SetLines(lines)

    # Create tube filter
    tube_filter = vtk.vtkTubeFilter()
    tube_filter.SetInputData(polydata)
    tube_filter.SetRadius(tube_radius)
    tube_filter.SetNumberOfSides(24)
    tube_filter.SetVaryRadiusToVaryRadiusOff()
    tube_filter.CappingOn()

    # Create mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(tube_filter.GetOutputPort())

    # Create actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # Configure properties
    property = actor.GetProperty()
    property.SetColor(color)
    property.SetOpacity(opacity)

    # Enhanced opacity handling
    if opacity < 1.0:
        property.SetAmbient(0.1)
        property.SetDiffuse(0.6)
        property.SetSpecular(0.3)
        property.SetSpecularPower(100)
        property.SetOpacity(opacity)
        # Force translucent rendering
        actor.ForceTranslucentOn()
        actor.GetProperty().BackfaceCullingOff()
        # Set surface representation
        property.SetRepresentationToSurface()
        # Disable scalar visibility
        mapper.SetScalarVisibility(False)
        # Set Phong interpolation
        property.SetInterpolationToPhong()
        actor.Modified()
    else:
        property.SetAmbient(0.3)
        property.SetDiffuse(0.7)
        property.SetSpecular(0.2)
        property.SetSpecularPower(20)

    return actor


def calculate_adaptive_resolution(param_range, trace_spacing):
    """
    Calculates appropriate resolution based on parameter range and trace spacing.

    Parameters:
    -----------
    param_range : tuple
        Range of parameter (min, max)
    trace_spacing : float
        Spacing between traces

    Returns:
        int: Adaptive resolution value
    """
    range_size = param_range[1] - param_range[0]
    # Base resolution on range size and spacing, with minimum and maximum limits
    base_resolution = int(range_size / trace_spacing * 5)  # 5 points per trace spacing
    return max(50, min(500, base_resolution))  # Clamp between 50 and 500 points


def create_parametric_curve_points(
    parametric_function, fixed_param, is_u_curve, u_range, v_range, trace_spacing
):
    """
    Creates points for a parametric curve at constant u or v with adaptive resolution.
    Handles parametric functions that may return scalars or arrays.
    """
    if is_u_curve:
        resolution = calculate_adaptive_resolution(v_range, trace_spacing)
        u = np.full(resolution, fixed_param)
        v = np.linspace(v_range[0], v_range[1], resolution)
    else:
        resolution = calculate_adaptive_resolution(u_range, trace_spacing)
        u = np.linspace(u_range[0], u_range[1], resolution)
        v = np.full(resolution, fixed_param)

    # Call the parametric function
    x, y, z = parametric_function(u, v)

    # Convert scalar outputs to constant arrays if needed
    x = np.full(resolution, x) if np.isscalar(x) else x
    y = np.full(resolution, y) if np.isscalar(y) else y
    z = np.full(resolution, z) if np.isscalar(z) else z

    # Ensure all arrays have the same length
    if not (len(x) == len(y) == len(z)):
        raise ValueError(
            f"Inconsistent array lengths: x={len(x)}, y={len(y)}, z={len(z)}"
        )

    return np.column_stack([x, y, z])


def create_curve_polydata_with_clipping(points, global_bounds):
    """
    Creates VTK polydata for a curve with proper clipping to global bounds.

    Parameters:
    -----------
    points : numpy array
        Array of 3D points
    global_bounds : tuple
        (xmin, xmax, ymin, ymax, zmin, zmax)

    Returns:
        vtkPolyData object or None if no valid segments
    """
    if len(points) < 2:
        return None

    # Check which points are within bounds
    in_bounds = np.all(
        [
            (points[:, 0] >= global_bounds[0]) & (points[:, 0] <= global_bounds[1]),
            (points[:, 1] >= global_bounds[2]) & (points[:, 1] <= global_bounds[3]),
            (points[:, 2] >= global_bounds[4]) & (points[:, 2] <= global_bounds[5]),
        ],
        axis=0,
    )

    # Find segments where at least one point is in bounds
    valid_segments = []
    for i in range(len(points) - 1):
        p1_in = in_bounds[i]
        p2_in = in_bounds[i + 1]

        if p1_in or p2_in:
            p1 = points[i]
            p2 = points[i + 1]

            # If both points are in bounds, add segment as is
            if p1_in and p2_in:
                valid_segments.append((p1, p2))
            # If only one point is in bounds, clip the segment
            else:
                t_values = []
                for dim in range(3):
                    dim_min = global_bounds[2 * dim]
                    dim_max = global_bounds[2 * dim + 1]

                    if p2[dim] != p1[dim]:
                        t1 = (dim_min - p1[dim]) / (p2[dim] - p1[dim])
                        t2 = (dim_max - p1[dim]) / (p2[dim] - p1[dim])
                        t_values.extend([t for t in [t1, t2] if 0 <= t <= 1])

                if t_values:
                    t_values = [
                        0 if p1_in else min(t_values),
                        1 if p2_in else max(t_values),
                    ]
                    clipped_p1 = p1 + t_values[0] * (p2 - p1)
                    clipped_p2 = p1 + t_values[1] * (p2 - p1)
                    valid_segments.append((clipped_p1, clipped_p2))

    if not valid_segments:
        return None

    # Create polydata from valid segments
    polydata = vtk.vtkPolyData()
    vtk_points = vtk.vtkPoints()
    lines = vtk.vtkCellArray()

    point_id = 0
    for p1, p2 in valid_segments:
        vtk_points.InsertNextPoint(p1)
        vtk_points.InsertNextPoint(p2)

        line = vtk.vtkLine()
        line.GetPointIds().SetId(0, point_id)
        line.GetPointIds().SetId(1, point_id + 1)
        lines.InsertNextCell(line)
        point_id += 2

    polydata.SetPoints(vtk_points)
    polydata.SetLines(lines)
    return polydata


def create_parametric_surface_traces_actor(
    parametric_function,  # NumPy function (u,v) -> (x,y,z)
    u_range=(0, 1),
    v_range=(0, 1),
    global_bounds=(X_MIN, X_MAX, Y_MIN, Y_MAX, Z_MIN, Z_MAX),
    trace_spacing=0.1,
    color=vtk.vtkNamedColors().GetColor3d("charcoal"),
    thickness=2,
    opacity=1.0,
):
    """
    Creates a VTK actor for parametric surface traces. The traces are created by
    evaluating the parametric function at different u and v values with trace_spacing
    between them. The result is a wireframe representation of the surface. The resultant
    traces curve is clipped to the global_bounds given in x,y,z coordinates. The function
    returns a VTK actor for the traces that can be added to the renderer.
    """
    if trace_spacing == 0 or thickness == 0 or opacity == 0:
        return None
    trace_spacing = abs(trace_spacing)

    append_filter = vtk.vtkAppendPolyData()

    # Create u-constant curves
    u_values = np.arange(u_range[0], u_range[1] + trace_spacing, trace_spacing)
    for u in u_values:
        points = create_parametric_curve_points(
            parametric_function, u, True, u_range, v_range, trace_spacing
        )
        curve_data = create_curve_polydata_with_clipping(points, global_bounds)
        if curve_data:
            append_filter.AddInputData(curve_data)

    # Create v-constant curves
    v_values = np.arange(v_range[0], v_range[1] + trace_spacing, trace_spacing)
    for v in v_values:
        points = create_parametric_curve_points(
            parametric_function, v, False, u_range, v_range, trace_spacing
        )
        curve_data = create_curve_polydata_with_clipping(points, global_bounds)
        if curve_data:
            append_filter.AddInputData(curve_data)

    append_filter.Update()

    # Create mapper and actor
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(append_filter.GetOutputPort())
    mapper.ScalarVisibilityOff()

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # Set up properties
    properties = actor.GetProperty()
    properties.SetColor(color)
    properties.SetLineWidth(thickness)
    properties.SetRepresentationToWireframe()
    properties.LightingOff()
    properties.SetAmbient(1.0)
    properties.SetDiffuse(0.0)
    properties.SetSpecular(0.0)
    properties.SetOpacity(opacity)
    properties.SetRenderLinesAsTubes(True)

    return actor


def create_horizontal_contours_actor(
    implicit_func,
    bounds,
    space=1,
    thickness=2,
    color=COLORS.GetColor3d("charcoal"),
    opacity=1.0,
    resolution=50,
):
    """
    Creates a VTK actor for horizontal contour traces of an implicit function.
    Each contour represents points where the function equals zero at a specific z-level.

    Parameters:
    -----------
    implicit_func : callable
        Vectorized function that takes x, y, z arrays and returns function values
    bounds : tuple
        The bounds of the function (xmin, xmax, ymin, ymax, zmin, zmax)
    space : float
        The vertical space between contour levels
    thickness : int
        Thickness of the contour lines
    color : tuple
        RGB values (0-1) for the contours
    opacity : float
        Transparency of the contours (0 = fully opaque, 1 = fully transparent)
    resolution : int
        The resolution of each contour curve

    Returns:
        vtkActor object or None if invalid parameters
    """
    if space == 0 or thickness == 0 or opacity == 0:
        return None
    space = abs(space)

    # Create append filter to combine all contours
    append_filter = vtk.vtkAppendPolyData()

    # Create horizontal plane points for each z-level
    z_values = np.arange(bounds[4], bounds[5] + space, space)

    for z in z_values:
        # Create grid points in the x-y plane
        x = np.linspace(bounds[0], bounds[1], resolution)
        y = np.linspace(bounds[2], bounds[3], resolution)
        X, Y = np.meshgrid(x, y, indexing="ij")
        Z = np.full_like(X, z)

        # Evaluate function on the grid
        points = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1)
        values = evaluate_function_on_points(points, implicit_func)

        # Create contour polydata
        contour_data = create_contour_polydata(points, values, resolution)
        if contour_data is not None:
            append_filter.AddInputData(contour_data)

    append_filter.Update()

    # Create mapper and configure visualization
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(append_filter.GetOutputPort())
    mapper.ScalarVisibilityOff()

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # Set up properties for appearance
    properties = actor.GetProperty()
    properties.SetColor(color)
    properties.SetLineWidth(thickness)
    properties.SetRepresentationToWireframe()
    properties.LightingOff()
    properties.SetAmbient(1.0)
    properties.SetDiffuse(0.0)
    properties.SetSpecular(0.0)
    properties.SetOpacity(opacity)
    properties.SetRenderLinesAsTubes(True)

    return actor


def create_parametric_horizontal_contours_actor(
    parametric_function,  # NumPy function (u,v) -> (x,y,z)
    u_range=(0, 1),
    v_range=(0, 1),
    global_bounds=(X_MIN, X_MAX, Y_MIN, Y_MAX, Z_MIN, Z_MAX),
    trace_spacing=0.1,
    color=vtk.vtkNamedColors().GetColor3d("charcoal"),
    thickness=2,
    opacity=1.0,
):
    """
    Creates a VTK actor for horizontal contour traces of a parametric surface.
    Each contour represents the intersection of the surface with horizontal planes
    at different z-levels.

    Parameters:
    -----------
    parametric_function : callable
        NumPy function that takes u, v arrays and returns x, y, z coordinates
    u_range : tuple
        The range of the u parameter (u_min, u_max)
    v_range : tuple
        The range of the v parameter (v_min, v_max)
    global_bounds : tuple
        The bounds for clipping (xmin, xmax, ymin, ymax, zmin, zmax)
    trace_spacing : float
        The vertical space between contour levels
    color : tuple
        RGB values (0-1) for the contours
    thickness : int
        Thickness of the contour lines
    opacity : float
        Transparency of the contours (0 = fully opaque, 1 = fully transparent)

    Returns:
        vtkActor object or None if invalid parameters
    """
    if trace_spacing == 0 or thickness == 0 or opacity == 0:
        return None
    trace_spacing = abs(trace_spacing)

    def find_intersections(v_fixed, z_level):
        """
        Finds intersection points along a constant-v curve with a horizontal plane.
        Returns u-values where the curve intersects the z_level plane.
        """
        # Create a dense sampling of u values
        u_samples = np.linspace(u_range[0], u_range[1], 200)
        v_samples = np.full_like(u_samples, v_fixed)
        
        # Evaluate the parametric function
        x, y, z = parametric_function(u_samples, v_samples)
        
        # Find where the curve crosses the z_level
        signs = np.sign(z - z_level)
        sign_changes = signs[:-1] * signs[1:] <= 0
        
        intersection_points = []
        for i in range(len(sign_changes)):
            if sign_changes[i]:
                # Linear interpolation to find more precise u value
                u1, u2 = u_samples[i], u_samples[i + 1]
                z1, z2 = z[i], z[i + 1]
                t = (z_level - z1) / (z2 - z1)
                u_intersect = u1 + t * (u2 - u1)
                
                # Evaluate the exact point
                x_int, y_int, z_int = parametric_function(
                    np.array([u_intersect]), 
                    np.array([v_fixed])
                )
                
                # Check if point is within bounds
                if (global_bounds[0] <= x_int <= global_bounds[1] and
                    global_bounds[2] <= y_int <= global_bounds[3]):
                    intersection_points.append((u_intersect, v_fixed))
        
        return intersection_points

    append_filter = vtk.vtkAppendPolyData()
    
    # Generate z-levels
    z_levels = np.arange(global_bounds[4], global_bounds[5] + trace_spacing, trace_spacing)
    
    # Calculate appropriate number of v-curves based on surface complexity
    v_resolution = int(max(50, min(200, 1/trace_spacing)))
    v_values = np.linspace(v_range[0], v_range[1], v_resolution)

    for z_level in z_levels:
        # Collect intersection points for this z-level
        level_points = []
        for v in v_values:
            intersections = find_intersections(v, z_level)
            level_points.extend(intersections)
            
        if not level_points:
            continue
            
        # Sort points to form continuous contour(s)
        contours = []
        current_contour = []
        
        # Convert parametric points to 3D coordinates
        points_array = np.array(level_points)
        if len(points_array) > 0:
            x, y, z = parametric_function(points_array[:, 0], points_array[:, 1])
            xyz_points = np.column_stack([x, y, z])
            
            # Create polydata for this contour
            if len(xyz_points) >= 2:
                polydata = create_curve_polydata_with_clipping(xyz_points, global_bounds)
                if polydata is not None:
                    append_filter.AddInputData(polydata)

    append_filter.Update()
    
    # Create mapper and actor
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(append_filter.GetOutputPort())
    mapper.ScalarVisibilityOff()
    
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    
    # Set up properties for appearance
    properties = actor.GetProperty()
    properties.SetColor(color)
    properties.SetLineWidth(thickness)
    properties.SetRepresentationToWireframe()
    properties.LightingOff()
    properties.SetAmbient(1.0)
    properties.SetDiffuse(0.0)
    properties.SetSpecular(0.0)
    properties.SetOpacity(opacity)
    properties.SetRenderLinesAsTubes(True)
    
    return actor