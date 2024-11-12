"""
Constants used throughout the application.
"""

from vtkmodules.vtkCommonColor import vtkNamedColors

# Window settings
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 1200
SLIDER_START_X = 80
SLIDER_WIDTH = 200
SLIDER_HEIGHT = 40

# Colors
colors = vtkNamedColors()
dark_blue = map(lambda x: x / 255.0, [26, 51, 102, 255])
colors.SetColor("dark_blue", *dark_blue)
