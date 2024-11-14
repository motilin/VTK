"""
Constants used throughout the application.
"""

from vtkmodules.vtkCommonColor import vtkNamedColors

# Window settings
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 1200
AXES_LENGTH = 5
X_MIN, X_MAX, Y_MIN, Y_MAX, Z_MIN, Z_MAX = -10, 10, -10, 10, -10, 10
CONTROL_PANEL_WIDTH = 300
CONTROL_PANEL_SPACING = 20

"""
Carefully curated color palette for mathematical surfaces.
The vtkNamedColors object contains the defined colors.
To access it use: colors.GetColor3d("color_name")
"""

colors = vtkNamedColors()

# Basic colors
dark_blue = map(lambda x: x / 255.0, [26, 51, 102, 255])
blue = map(lambda x: x / 255.0, [0, 0, 255, 255])
red = map(lambda x: x / 255.0, [255, 0, 0, 255])

# Deep blues and teals
deep_azure = map(lambda x: x / 255.0, [0, 127, 255, 255])  # Rich blue
midnight_blue = map(lambda x: x / 255.0, [25, 25, 112, 255])  # Very deep blue
teal = map(lambda x: x / 255.0, [0, 128, 128, 255])  # Classic teal
prussian_blue = map(lambda x: x / 255.0, [0, 49, 83, 255])  # Dark sophisticated blue

# Purples and magentas
royal_purple = map(lambda x: x / 255.0, [120, 81, 169, 255])  # Rich purple
deep_magenta = map(lambda x: x / 255.0, [139, 0, 98, 255])  # Deep pink-purple
lavender = map(lambda x: x / 255.0, [150, 123, 182, 255])  # Soft purple

# Warm colors
burgundy = map(lambda x: x / 255.0, [128, 0, 32, 255])  # Deep red
coral = map(lambda x: x / 255.0, [255, 127, 80, 255])  # Warm orange-pink
amber = map(lambda x: x / 255.0, [255, 191, 0, 255])  # Golden yellow

# Cool greens
emerald = map(lambda x: x / 255.0, [46, 125, 50, 255])  # Rich green
sage = map(lambda x: x / 255.0, [106, 153, 78, 255])  # Muted green
forest_green = map(lambda x: x / 255.0, [34, 139, 34, 255])  # Deep green

# Neutral metallics
gunmetal = map(lambda x: x / 255.0, [44, 53, 57, 255])  # Dark gray-blue
platinum = map(lambda x: x / 255.0, [229, 228, 226, 255])  # Light metallic
bronze = map(lambda x: x / 255.0, [205, 127, 50, 255])  # Warm metallic

# Set all colors
colors.SetColor("deep_azure", *deep_azure)
colors.SetColor("midnight_blue", *midnight_blue)
colors.SetColor("teal", *teal)
colors.SetColor("prussian_blue", *prussian_blue)
colors.SetColor("royal_purple", *royal_purple)
colors.SetColor("deep_magenta", *deep_magenta)
colors.SetColor("lavender", *lavender)
colors.SetColor("burgundy", *burgundy)
colors.SetColor("coral", *coral)
colors.SetColor("amber", *amber)
colors.SetColor("emerald", *emerald)
colors.SetColor("sage", *sage)
colors.SetColor("forest_green", *forest_green)
colors.SetColor("gunmetal", *gunmetal)
colors.SetColor("platinum", *platinum)
colors.SetColor("bronze", *bronze)
colors.SetColor("dark_blue", *dark_blue)
colors.SetColor("blue", *blue)
colors.SetColor("red", *red)
