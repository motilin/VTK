from PyQt5.QtWidgets import QLabel, QPushButton, QHBoxLayout, QColorDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from vtkmodules.vtkCommonDataModel import vtkColor3d

def vtk_to_qcolor(vtk_color):
    """Convert vtkColor3d to QColor."""
    return QColor(int(vtk_color.GetRed() * 255), 
                 int(vtk_color.GetGreen() * 255), 
                 int(vtk_color.GetBlue() * 255))

def qcolor_to_vtk(qcolor):
    """Convert QColor to vtkColor3d."""
    vtk_color = vtkColor3d()
    vtk_color.SetRed(qcolor.red() / 255.0)
    vtk_color.SetGreen(qcolor.green() / 255.0)
    vtk_color.SetBlue(qcolor.blue() / 255.0)
    return vtk_color

def set_color(color_picker, color):
    """Set the color of a color picker button."""
    qcolor = vtk_to_qcolor(color)
    color_picker.setStyleSheet(f"background-color: {qcolor.name()}")

class ColorPicker:
    def __init__(self, parent, text, color, callback, dual=False):
        self.parent = parent
        self.label = QLabel(text, parent)
        self.pickers = [QPushButton(parent) for _ in range(1 if not dual else 2)]
        self.callbacks = [callback] if not dual else list(callback)
        self.colors = [color] if not dual else list(color)
        self.dual = dual
        
        self._setup_pickers()
        self._setup_layout()
        
    def _setup_pickers(self):
        """Configure the color picker buttons."""
        for picker, color in zip(self.pickers, self.colors):
            picker.setFixedSize(50, 20)
            set_color(picker, color)
            
        def create_color_handler(picker_idx):
            def handler():
                initial_color = self.colors[picker_idx]  # Use current color as initial
                qcolor = QColorDialog.getColor(
                    vtk_to_qcolor(initial_color), 
                    self.parent
                )
                if qcolor.isValid():
                    new_color = qcolor_to_vtk(qcolor)
                    # Update the stored color
                    self.colors[picker_idx] = new_color
                    # Update the button appearance
                    set_color(self.pickers[picker_idx], new_color)
                    # Call the callback with the new color
                    self.callbacks[picker_idx](new_color)
            return handler
            
        for i, picker in enumerate(self.pickers):
            picker.clicked.connect(create_color_handler(i))
    
    def _setup_layout(self):
        """Create and setup the layout."""
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.label, alignment=Qt.AlignLeft)
        for picker in self.pickers:
            self.layout.addWidget(picker, alignment=Qt.AlignRight)
    
    def set_colors(self, colors):
        """Set the color(s) for the picker(s)."""
        colors = [colors] if not self.dual else list(colors)
        for i, color in enumerate(colors):
            set_color(self.pickers[i], color)
            self.colors[i] = color
    
    def get_colors(self):
        """Get the current color(s) from the picker(s)."""
        return self.colors[0] if not self.dual else tuple(self.colors)
