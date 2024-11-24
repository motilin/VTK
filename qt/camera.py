import vtk
import json
import numpy as np

class VTKCameraManager:
    """
    A utility class to save and restore complete VTK camera states.
    """
    @staticmethod
    def save_camera_state(renderer):
        """
        Save all essential camera parameters from a VTK renderer.
        
        Args:
            renderer: vtkRenderer object
            
        Returns:
            dict: Complete camera state
        """
        camera = renderer.GetActiveCamera()
        
        # Calculate aspect ratio from renderer
        if renderer.GetRenderWindow():
            size = renderer.GetRenderWindow().GetSize()
            aspect = size[0] / size[1] if size[1] != 0 else 1.0
        else:
            aspect = 1.0
            
        camera_state = {
            # Camera position and orientation
            "position": camera.GetPosition(),
            "focal_point": camera.GetFocalPoint(),
            "view_up": camera.GetViewUp(),
            
            # View angle and clipping range
            "view_angle": camera.GetViewAngle(),
            "clipping_range": camera.GetClippingRange(),
            
            # Additional parameters for exact reproduction
            "parallel_projection": camera.GetParallelProjection(),
            "parallel_scale": camera.GetParallelScale(),
            
            # Distance parameters
            "distance": camera.GetDistance(),
            "roll": camera.GetRoll(),
            
            # View transform (doesn't require aspect ratio)
            "view_transform": list(camera.GetViewTransformMatrix().GetData()),
            
            # Projection transform with aspect ratio
            "projection_transform": list(camera.GetProjectionTransformMatrix(aspect, -1, 1).GetData()),
            
            # Store aspect ratio for restoration
            "aspect_ratio": aspect,
            
            # Renderer parameters that affect view
            "viewport": renderer.GetViewport(),
            "background": renderer.GetBackground()
        }
        
        return camera_state

    @staticmethod
    def load_camera_state(renderer, camera_state):
        """
        Restore camera state to a VTK renderer.
        
        Args:
            renderer: vtkRenderer object
            camera_state: dict containing camera parameters
        """
        camera = renderer.GetActiveCamera()
        
        # Set basic position and orientation
        camera.SetPosition(camera_state["position"])
        camera.SetFocalPoint(camera_state["focal_point"])
        camera.SetViewUp(camera_state["view_up"])
        
        # Set view properties
        camera.SetViewAngle(camera_state["view_angle"])
        camera.SetClippingRange(camera_state["clipping_range"])
        
        # Set projection type and scale
        camera.SetParallelProjection(camera_state["parallel_projection"])
        camera.SetParallelScale(camera_state["parallel_scale"])
        
        # Set additional parameters
        camera.SetDistance(camera_state["distance"])
        camera.SetRoll(camera_state["roll"])
        
        # Set renderer properties
        renderer.SetViewport(camera_state["viewport"])
        renderer.SetBackground(camera_state["background"])
        
        # Force update
        renderer.ResetCameraClippingRange()
        renderer.Render()

    @staticmethod
    def save_to_file(renderer, filename):
        """
        Save camera state to a JSON file.
        
        Args:
            renderer: vtkRenderer object
            filename: str, path to save the JSON file
        """
        camera_state = VTKCameraManager.save_camera_state(renderer)
        
        # Convert numpy arrays and tuples to lists for JSON serialization
        serializable_state = {}
        for key, value in camera_state.items():
            if isinstance(value, (np.ndarray, tuple)):
                serializable_state[key] = list(value)
            else:
                serializable_state[key] = value
        
        with open(filename, 'w') as f:
            json.dump(serializable_state, f, indent=4)

    @staticmethod
    def load_from_file(renderer, filename):
        """
        Load camera state from a JSON file.
        
        Args:
            renderer: vtkRenderer object
            filename: str, path to the JSON file
        """
        with open(filename, 'r') as f:
            camera_state = json.load(f)
            
        # Convert lists back to tuples for VTK
        for key in ["position", "focal_point", "view_up", "clipping_range", "viewport", "background"]:
            if key in camera_state:
                camera_state[key] = tuple(camera_state[key])
                
        VTKCameraManager.load_camera_state(renderer, camera_state)
