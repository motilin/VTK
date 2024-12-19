from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QShortcut
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt
import sys, logging, vtk
from src.core.interactor import (
    set_mathematical_view,
    set_mathematical_2d_view,
    export_to_obj,
    export_to_png,
    export_to_html,
)
from src.core.constants import WINDOW_WIDTH, WINDOW_HEIGHT
from qt.command_palette import CommandPalette
from src.core.constants import DEGREES_OF_ROTATION


class VTKMainWindow(QMainWindow):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.init_ui()
        self.setup_shortcuts()

    def init_ui(self):
        self.setWindowTitle("Function Plotter")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.widget)

        if (
            not hasattr(self.widget.vtk_widget, "renderer")
            or not self.widget.vtk_widget.renderer
        ):
            logging.warning("No renderer found, initializing a new one")
            self.widget.vtk_widget.renderer = vtk.vtkRenderer()
            self.widget.vtk_widget.get_render_window().AddRenderer(
                self.widget.vtk_widget.renderer
            )

        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.show()
        self.raise_()
        self.activateWindow()

    def setup_shortcuts(self):
        quit_shortcut = QShortcut(QKeySequence(Qt.Key_Q), self)
        quit_shortcut.activated.connect(self.close_application)

        reset_view_shortcut = QShortcut(QKeySequence(Qt.Key_R), self)
        reset_view_shortcut.activated.connect(self.reset_mathematical_view)

        set_2d_view_shortcut = QShortcut(QKeySequence(Qt.Key_X), self)
        set_2d_view_shortcut.activated.connect(self.set_2d_view)

        # use the / key to focus the input box
        input_box_focus_shortcut = QShortcut(QKeySequence(Qt.Key_Slash), self)
        input_box_focus_shortcut.activated.connect(self.focus_input_box)

        # use the Ctrl+Shift+P shortcut to show the command palette
        palette_shortcut = QShortcut(QKeySequence("Ctrl+Shift+P"), self)
        palette_shortcut.activated.connect(self.show_command_palette)

        # shortcuts for camera rotation
        rotate_left_shortcut = QShortcut(QKeySequence(Qt.Key_L), self)
        rotate_left_shortcut.activated.connect(self.rotate_left)

        rotate_right_shortcut = QShortcut(QKeySequence(Qt.Key_H), self)
        rotate_right_shortcut.activated.connect(self.rotate_right)

        rotate_up_shortcut = QShortcut(QKeySequence(Qt.Key_J), self)
        rotate_up_shortcut.activated.connect(self.rotate_up)

        rotate_down_shortcut = QShortcut(QKeySequence(Qt.Key_K), self)
        rotate_down_shortcut.activated.connect(self.rotate_down)
        
        # Roll rotation shortcuts using arrow keys
        roll_clockwise_shortcut = QShortcut(QKeySequence(Qt.Key_Left), self)
        roll_clockwise_shortcut.activated.connect(self.roll_counterclockwise)

        roll_counterclockwise_shortcut = QShortcut(QKeySequence(Qt.Key_Right), self)
        roll_counterclockwise_shortcut.activated.connect(self.roll_clockwise)

    def close_application(self):
        self.close()
        sys.exit()

    def reset_mathematical_view(self):
        if (
            hasattr(self.widget.vtk_widget, "renderer")
            and self.widget.vtk_widget.renderer
        ):
            set_mathematical_view(self.widget.vtk_widget.renderer)
            self.widget.vtk_widget.get_render_window().Render()
        else:
            logging.warning("No renderer found, cannot reset view")

    def set_2d_view(self):
        if (
            hasattr(self.widget.vtk_widget, "renderer")
            and self.widget.vtk_widget.renderer
        ):
            set_mathematical_2d_view(self.widget.vtk_widget.renderer)
            self.widget.vtk_widget.get_render_window().Render()
        else:
            logging.warning("No renderer found, cannot set 2 view")

    def export_obj(self, filename):
        export_to_obj(self.widget.vtk_widget, "output")

    def export_png(self, filename):
        export_to_png(self.widget.vtk_widget, "output")

    def export_html(self, filename):
        export_to_html(self.widget.vtk_widget, "output")

    def focus_input_box(self):
        self.widget.control_widget.input_box.setFocus()
        self.widget.control_widget.input_box.selectAll()
        self.widget.control_widget.input_box.setFocus()

    def save_state(self, filename):
        pass

    def load_state(self, filename):
        pass

    def show_command_palette(self):
        palette = CommandPalette(self)
        palette.exec_()

    def rotate_left(self) -> None:
        """Rotates the scene clockwise (camera moves left)."""
        self.rotate_camera_horizontal(clockwise=True)

    def rotate_right(self) -> None:
        """Rotates the scene counterclockwise (camera moves right)."""
        self.rotate_camera_horizontal(clockwise=False)

    def rotate_up(self) -> None:
        """Rotates the scene upward."""
        self.rotate_camera_vertical(upward=True)

    def rotate_down(self) -> None:
        """Rotates the scene downward."""
        self.rotate_camera_vertical(upward=False)

    def roll_clockwise(self) -> None:
        """Rotates the view clockwise around the view direction."""
        self.rotate_camera_roll(clockwise=True)

    def roll_counterclockwise(self) -> None:
        """Rotates the view counterclockwise around the view direction."""
        self.rotate_camera_roll(clockwise=False)

    def rotate_camera_horizontal(self, clockwise: bool = True) -> None:
        """
        Rotates the camera horizontally around the scene's center point.

        The camera maintains its vertical position and distance from the center while
        moving along the horizontal plane. The camera view remains fixed on the center point.

        Args:
            clockwise (bool): Direction of rotation. True for clockwise, False for counterclockwise.
        """
        if not hasattr(self.widget.vtk_widget, "renderer"):
            logging.warning("No renderer found, cannot rotate camera")
            return

        camera = self.widget.vtk_widget.renderer.GetActiveCamera()

        # Get current camera position and properties
        pos = list(camera.GetPosition())
        focal = list(camera.GetFocalPoint())

        # Calculate rotation angle (negative for clockwise due to VTK's coordinate system)
        angle = -DEGREES_OF_ROTATION if clockwise else DEGREES_OF_ROTATION

        # Create transformation matrix for rotation around Z axis
        transform = vtk.vtkTransform()
        transform.PostMultiply()
        transform.Translate(-focal[0], -focal[1], -focal[2])  # Move to origin
        transform.RotateZ(angle)  # Rotate around Z axis
        transform.Translate(focal[0], focal[1], focal[2])  # Move back

        # Apply transformation to camera position
        new_pos = transform.TransformPoint(pos)
        camera.SetPosition(new_pos)

        # Update the render
        self.widget.vtk_widget.get_render_window().Render()

    def rotate_camera_vertical(self, upward: bool = True) -> None:
        """
        Rotates the camera vertically around the scene's center point.

        The camera maintains its distance from the center while moving in a vertical arc.
        The camera view remains fixed on the center point, and the camera maintains its
        relative orientation without flipping.

        Args:
            upward (bool): Direction of rotation. True for upward, False for downward.
        """
        if not hasattr(self.widget.vtk_widget, "renderer"):
            logging.warning("No renderer found, cannot rotate camera")
            return

        camera = self.widget.vtk_widget.renderer.GetActiveCamera()

        # Get current camera position and properties
        pos = list(camera.GetPosition())
        focal = list(camera.GetFocalPoint())
        up = list(camera.GetViewUp())

        # Calculate rotation angle
        angle = DEGREES_OF_ROTATION if upward else -DEGREES_OF_ROTATION

        # Calculate the right vector (perpendicular to view direction and up vector)
        # This will be our rotation axis
        view_direction = [focal[0] - pos[0], focal[1] - pos[1], focal[2] - pos[2]]

        # Normalize view direction
        length = (
            view_direction[0] ** 2 + view_direction[1] ** 2 + view_direction[2] ** 2
        ) ** 0.5
        view_direction = [v / length for v in view_direction]

        # Calculate right vector using cross product of up vector and view direction
        right_vector = [
            up[1] * view_direction[2] - up[2] * view_direction[1],
            up[2] * view_direction[0] - up[0] * view_direction[2],
            up[0] * view_direction[1] - up[1] * view_direction[0],
        ]

        # Normalize right vector
        length = (
            right_vector[0] ** 2 + right_vector[1] ** 2 + right_vector[2] ** 2
        ) ** 0.5
        right_vector = [v / length for v in right_vector]

        # Create transformation matrix for rotation around the right vector
        transform = vtk.vtkTransform()
        transform.PostMultiply()
        transform.Translate(-focal[0], -focal[1], -focal[2])  # Move to origin
        transform.RotateWXYZ(
            angle, right_vector[0], right_vector[1], right_vector[2]
        )  # Rotate around right vector
        transform.Translate(focal[0], focal[1], focal[2])  # Move back

        # Apply transformation to camera position
        new_pos = transform.TransformPoint(pos)
        camera.SetPosition(new_pos)

        # Calculate and set the new up vector
        new_up = transform.TransformVector(up)
        camera.SetViewUp(new_up)

        # Update the render
        self.widget.vtk_widget.get_render_window().Render()

    def rotate_camera_roll(self, clockwise: bool = True) -> None:
        """
        Rotates the camera around its view direction (roll rotation).

        This creates the effect of rotating the entire view as if rotating the screen.
        The camera position and focal point remain unchanged, only the up vector is modified.

        Args:
            clockwise (bool): Direction of rotation. True for clockwise, False for counterclockwise.
        """
        if not hasattr(self.widget.vtk_widget, "renderer"):
            logging.warning("No renderer found, cannot rotate camera")
            return

        camera = self.widget.vtk_widget.renderer.GetActiveCamera()

        # Get current camera properties
        pos = list(camera.GetPosition())
        focal = list(camera.GetFocalPoint())
        up = list(camera.GetViewUp())

        # Calculate view direction
        view_direction = [focal[0] - pos[0], focal[1] - pos[1], focal[2] - pos[2]]

        # Normalize view direction
        length = (
            view_direction[0] ** 2 + view_direction[1] ** 2 + view_direction[2] ** 2
        ) ** 0.5
        view_direction = [v / length for v in view_direction]

        # Calculate rotation angle (negative for clockwise to match screen rotation direction)
        angle = -DEGREES_OF_ROTATION if clockwise else DEGREES_OF_ROTATION

        # Create transformation matrix for rotation around view direction
        transform = vtk.vtkTransform()
        transform.PostMultiply()
        transform.RotateWXYZ(
            angle, view_direction[0], view_direction[1], view_direction[2]
        )

        # Apply transformation to up vector only
        new_up = transform.TransformVector(up)
        camera.SetViewUp(new_up)

        # Update the render
        self.widget.vtk_widget.get_render_window().Render()