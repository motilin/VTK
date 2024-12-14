"""
Custom interactor styles and related functionality.
"""

import vtk, os, sys, json
from vtk import vtkOBJExporter
from pathlib import Path
import base64


# Define the custom interactor style
class CustomInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.AddObserver(
            vtk.vtkCommand.LeftButtonPressEvent, self.left_button_press_event
        )
        # self.AddObserver(vtk.vtkCommand.KeyPressEvent, self.on_key_press_event)

    def left_button_press_event(self, obj, event):
        self.OnLeftButtonDown()
        return

    def on_key_press_event(self, obj, event):
        key = self.GetInteractor().GetKeySym()
        # if key == "q":
        #     self.GetInteractor().GetRenderWindow().Finalize()
        #     self.GetInteractor().TerminateApp()
        #     sys.exit(0)
        # if key == "r":
        #     set_mathematical_view(self.widget.renderer)
        # if key == "o":
        #     export_to_obj(self.widget, "output")
        # if key == "p":
        #     export_to_png(self.widget, "output")


def set_mathematical_view(renderer):
    """
    Sets up the classic mathematical textbook view where:
    - X axis points left
    - Y axis points right
    - Z axis points up
    - XY plane is horizontal
    - View is straight-on to the XZ plane

    Parameters:
    -----------
    renderer : vtkRenderer
        The renderer whose camera will be transformed
    """
    # Get the camera
    camera = renderer.GetActiveCamera()

    # Reset the camera first
    camera.SetPosition(0, 1, 0)  # Position along negative Y axis
    camera.SetViewUp(0, 0, 1)  # Z axis points up
    camera.SetFocalPoint(0, 0, 0)  # Looking at origin

    # Optional: adjust for better initial view
    camera.Elevation(20)  # Slight elevation to see 3D better
    camera.Azimuth(-45)  # Slight rotation to enhance 3D perspective

    # Reset the camera to fit all actors
    renderer.ResetCamera()


def set_mathematical_2d_view(renderer):
    """
    Sets up a classic 2D mathematical Cartesian view where:
    - X axis points right
    - Y axis points up
    - Z axis points towards the viewer
    - View is perfectly leveled for optimal 2D visualization

    Parameters:
    -----------
    renderer : vtkRenderer
        The renderer whose camera will be transformed to 2D view
    """
    # Get the camera
    camera = renderer.GetActiveCamera()

    # Set camera for a pure 2D orthographic projection
    camera.SetParallelProjection(True)  # Use orthographic projection

    # Position camera directly above the origin, looking down
    camera.SetPosition(0, 0, 1)  # Z axis pointing towards viewer
    camera.SetFocalPoint(0, 0, 0)  # Look at the origin
    camera.SetViewUp(0, 1, 0)  # Y axis points up

    # Adjust camera to ensure perfect 2D view
    camera.SetClippingRange(0.1, 10)  # Minimal clipping range for 2D

    # Reset the camera to fit all actors, but prevent any rotation
    renderer.ResetCamera()

    # Adjust parallel scale to ensure good fit
    camera.SetParallelScale(8)  # Can be adjusted based on your specific scene


def export_to_obj(widget, filepath):
    """
    Exports the current view of the renderer to an OBJ file.

    Parameters:
    -----------
    widget: QWidget
        The widget containing the renderer
    filepath : str
        The complete filepath where the OBJ file should be saved
        (including directory path and filename)
    """
    # Extract directory and basename from the full filepath
    directory = os.path.dirname(filepath)
    basename = os.path.splitext(os.path.basename(filepath))[0]

    # If directory doesn't exist, create it
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    # Construct the full path for the exporter
    # If directory is empty (current directory), just use basename
    file_prefix = os.path.join(directory, basename) if directory else basename

    # Set up and execute the export
    render_window = widget.interactor.GetRenderWindow()
    exporter = vtkOBJExporter()
    exporter.SetFilePrefix(file_prefix)
    exporter.SetInput(render_window)
    exporter.Write()


def export_to_png(widget, filepath):
    """
    Exports the current view of the renderer to a PNG file.

    Parameters:
    -----------
    widget: QWidget
        The widget containing the renderer
    filepath : str
        The complete filepath where the PNG file should be saved
        (including directory path and filename)
    """
    # Ensure the directory exists
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    # If the filepath doesn't end in .png, add it
    if not filepath.lower().endswith(".png"):
        filepath += ".png"

    # Set up and execute the export
    render_window = widget.interactor.GetRenderWindow()
    window_to_image_filter = vtk.vtkWindowToImageFilter()
    window_to_image_filter.SetInput(render_window)
    window_to_image_filter.Update()

    writer = vtk.vtkPNGWriter()
    writer.SetFileName(filepath)
    writer.SetInputConnection(window_to_image_filter.GetOutputPort())
    writer.Write()


def save_state(main_widget, filepath):
    """
    Saves the current state of the main widget to a file.
    main_widget : A subclass of QWidget, like PlotFunc
    filepath : str
    """
    if not filepath.lower().endswith(".json"):
        filepath += ".json"
    state = main_widget.marshalize()
    with open(filepath, "w") as file:
        json.dump(state, file, indent=4)


def load_state(main_widget, filepath):
    """
    Loads the state of the main widget from a file.
    """
    with open(filepath, "r") as file:
        state = json.load(file)
    main_widget.unmarshalize(state)


# Currently not working


def export_to_html(vtk_widget, output_path, title="VTK Visualization"):
    """
    Export a VTK render window to an interactive WebGL visualization
    that maintains VTK-like interaction capabilities.
    """
    try:
        # Get the render window and renderer
        render_window = vtk_widget.get_render_window()
        if not render_window:
            raise ValueError("Unable to get render window from widget")

        renderer = render_window.GetRenderers().GetFirstRenderer()
        if not renderer:
            raise ValueError("No renderer found in render window")

        # Extract scene data
        scene_data = {"actors": [], "camera": {}}

        # Get camera settings
        camera = renderer.GetActiveCamera()
        if not camera:
            raise ValueError("No active camera found in renderer")

        scene_data["camera"] = {
            "position": list(camera.GetPosition()),
            "focalPoint": list(camera.GetFocalPoint()),
            "viewUp": list(camera.GetViewUp()),
            "viewAngle": camera.GetViewAngle(),
        }

        # Process each actor in the scene
        actors = renderer.GetActors()
        actors.InitTraversal()
        actor = actors.GetNextItem()
        actor_count = 0

        while actor:
            actor_count += 1

            mapper = actor.GetMapper()
            if not mapper:
                actor = actors.GetNextItem()
                continue

            input_data = mapper.GetInput()
            if not input_data:
                actor = actors.GetNextItem()
                continue

            # Convert to polydata if needed
            if not isinstance(input_data, vtk.vtkPolyData):
                if hasattr(input_data, "GetOutput"):
                    input_data.Update()
                    poly_data = input_data.GetOutput()
                    if not poly_data:
                        actor = actors.GetNextItem()
                        continue
                else:
                    actor = actors.GetNextItem()
                    continue
            else:
                poly_data = input_data

            # Get points
            points = poly_data.GetPoints()
            if not points:
                actor = actors.GetNextItem()
                continue

            points_data = []
            n_points = points.GetNumberOfPoints()

            for i in range(n_points):
                point = points.GetPoint(i)
                points_data.append(list(point))

            # Get polys and verts
            polys = poly_data.GetPolys()
            verts = poly_data.GetVerts()
            polys_data = []

            # Process polygon cells
            if polys and polys.GetNumberOfCells() > 0:
                polys.InitTraversal()
                id_list = vtk.vtkIdList()

                while polys.GetNextCell(id_list):
                    cell = [id_list.GetId(j) for j in range(id_list.GetNumberOfIds())]
                    polys_data.append(cell)

            # Process vertex cells if no polygons
            elif verts and verts.GetNumberOfCells() > 0:
                verts.InitTraversal()
                id_list = vtk.vtkIdList()

                while verts.GetNextCell(id_list):
                    cell = [id_list.GetId(j) for j in range(id_list.GetNumberOfIds())]
                    polys_data.append(cell)

            # Get color properties
            prop = actor.GetProperty()
            color = list(prop.GetColor())
            opacity = prop.GetOpacity()
            point_size = prop.GetPointSize()

            actor_data = {
                "points": points_data,
                "polys": polys_data,
                "color": color,
                "opacity": opacity,
                "pointSize": point_size,
                "isPoints": bool(verts and verts.GetNumberOfCells() > 0),
            }
            scene_data["actors"].append(actor_data)

            actor = actors.GetNextItem()

        if not scene_data["actors"]:
            raise ValueError("No valid actors found in the scene")

        # Create HTML with VTK.js viewer
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body, html {{
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
        }}
        #viewer {{
            width: 100%;
            height: 100%;
            background: #000000;
        }}
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/vtk.js/25.7.1/vtk.js"></script>
</head>
<body>
    <div id="viewer"></div>
    <script>
        const rootContainer = document.querySelector('#viewer');
        
        const sceneData = {json.dumps(scene_data)};
        
        // Create the basic VTK.js pipeline
        const renderWindow = vtk.Rendering.Core.vtkRenderWindow.newInstance();
        const renderer = vtk.Rendering.Core.vtkRenderer.newInstance({{
            background: [0.1, 0.1, 0.1]
        }});
        renderWindow.addRenderer(renderer);
        
        // Create OpenGL rendering context
        const openglRenderWindow = vtk.Rendering.OpenGL.vtkRenderWindow.newInstance();
        renderWindow.addView(openglRenderWindow);
        
        // Set container and initialize size
        openglRenderWindow.setContainer(rootContainer);
        const dims = rootContainer.getBoundingClientRect();
        openglRenderWindow.setSize(dims.width, dims.height);
        
        // Setup interactor
        const interactor = vtk.Rendering.Core.vtkRenderWindowInteractor.newInstance();
        interactor.setView(openglRenderWindow);
        interactor.initialize();
        interactor.bindEvents(rootContainer);
        
        // Setup interactor style
        const interactorStyle = vtk.Interaction.Style.vtkInteractorStyleTrackballCamera.newInstance();
        interactor.setInteractorStyle(interactorStyle);
        
        // Setup camera
        const camera = renderer.getActiveCamera();
        const cameraData = sceneData.camera;
        camera.set({{
            position: cameraData.position,
            focalPoint: cameraData.focalPoint,
            viewUp: cameraData.viewUp,
            viewAngle: cameraData.viewAngle
        }});
        
        // Process each actor
        sceneData.actors.forEach((actorData, index) => {{
            const points = vtk.Common.Core.vtkPoints.newInstance();
            const pointsArray = Float64Array.from(actorData.points.flat());
            points.setData(pointsArray, 3);
            
            const polyData = vtk.Common.DataModel.vtkPolyData.newInstance();
            polyData.setPoints(points);
            
            if (actorData.isPoints) {{
                // Handle vertex data
                const verts = vtk.Common.Core.vtkCellArray.newInstance();
                const numPoints = actorData.points.length;
                const connectivity = new Uint32Array(numPoints);
                const offsets = new Uint32Array(numPoints);
                
                for (let i = 0; i < numPoints; i++) {{
                    connectivity[i] = i;
                    offsets[i] = i + 1;  // Cumulative offset
                }}
                
                verts.setData(connectivity, offsets, 1);
                polyData.setVerts(verts);
            }} else if (actorData.polys.length > 0) {{
                // Handle polygon data
                const polys = vtk.Common.Core.vtkCellArray.newInstance();
                const flatPolys = actorData.polys.flat();
                const npts = actorData.polys[0].length;
                const connectivity = new Uint32Array(flatPolys);
                const offsets = new Uint32Array(actorData.polys.length);
                
                for (let i = 0; i < actorData.polys.length; i++) {{
                    offsets[i] = (i + 1) * npts;  // Cumulative offset
                }}
                
                polys.setData(connectivity, offsets, npts);
                polyData.setPolys(polys);
            }}
            
            const mapper = vtk.Rendering.Core.vtkMapper.newInstance();
            mapper.setInputData(polyData);
            
            const actor = vtk.Rendering.Core.vtkActor.newInstance();
            actor.setMapper(mapper);
            
            const property = actor.getProperty();
            property.setColor(...actorData.color);
            property.setOpacity(actorData.opacity);
            
            if (actorData.isPoints) {{
                property.setPointSize(actorData.pointSize);
            }}
            
            renderer.addActor(actor);
        }});
        
        // Handle window resize
        function onResize() {{
            const dims = rootContainer.getBoundingClientRect();
            openglRenderWindow.setSize(dims.width, dims.height);
            renderWindow.render();
        }}
        
        window.addEventListener('resize', onResize);
        
        // Initial render
        renderer.resetCamera();
        renderWindow.render();
    </script>
</body>
</html>
"""

        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            f.write(html_content)

        return True

    except Exception as e:
        print(f"Error exporting scene: {str(e)}")
        import traceback

        traceback.print_exc()
        return False
