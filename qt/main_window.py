from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QShortcut
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt
import sys
from src.core.interactor import (
    set_mathematical_view,
    export_to_obj,
    export_to_png,
    export_to_html,
)
from src.core.constants import WINDOW_WIDTH, WINDOW_HEIGHT
from qt.command_palette import CommandPalette


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

        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.show()
        self.raise_()
        self.activateWindow()

    def setup_shortcuts(self):
        quit_shortcut = QShortcut(QKeySequence(Qt.Key_Q), self)
        quit_shortcut.activated.connect(self.close_application)

        reset_view_shortcut = QShortcut(QKeySequence(Qt.Key_R), self)
        reset_view_shortcut.activated.connect(self.reset_mathematical_view)

        # export_obj_shortcut = QShortcut(QKeySequence(Qt.Key_O), self)
        # export_obj_shortcut.activated.connect(self.export_obj)

        # export_png_shortcut = QShortcut(QKeySequence(Qt.Key_P), self)
        # export_png_shortcut.activated.connect(self.export_png)

        # use the / key to focus the input box
        input_box_focus_shortcut = QShortcut(QKeySequence(Qt.Key_Slash), self)
        input_box_focus_shortcut.activated.connect(self.focus_input_box)

        # use the Ctrl+Shift+P shortcut to show the command palette
        palette_shortcut = QShortcut(QKeySequence("Ctrl+Shift+P"), self)
        palette_shortcut.activated.connect(self.show_command_palette)

    def close_application(self):
        self.close()
        sys.exit()

    def reset_mathematical_view(self):
        set_mathematical_view(self.widget.renderer)
        self.widget.vtk_widget.get_render_window().Render()

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
