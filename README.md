# Mathematical Visualization Tool

A 3D visualization tool for mathematical objects including implicit surfaces, parametric curves, parametric surfaces, and points in 3D space. The application supports real-time rendering with customizable visual properties and advanced mathematical operations.

## Features

### Supported Mathematical Objects

1. **Implicit Surfaces**
   - Equations of the form f(x,y,z) = 0
   - Supports arbitrary mathematical expressions involving x, y, and z variables
   - Automatically handles complex mathematical operations and simplifications

2. **Parametric Curves**
   - Vector-valued functions r(t) = [x(t), y(t), z(t)]
   - Defined using Matrix notation or vector functions
   - Support for computing differential geometry properties

3. **Parametric Surfaces**
   - Vector-valued functions r(u,v) = [x(u,v), y(u,v), z(u,v)]
   - Two-parameter representations using u and v variables
   - Surface visualization with customizable properties

4. **Points**
   - Static points in 3D space
   - Represented as constant vectors

### Visualization Features

- Real-time 3D rendering
- Customizable visual properties:
  - Color gradients (color_start, color_end)
  - Line colors
  - Opacity
  - Thickness
  - Trace spacing
  - Dash spacing
- Toggle between surface and line representations
- Automatic bounds detection and adjustment
- Safe handling of complex numbers and undefined regions

### Mathematical Operations

The tool includes several built-in mathematical functions for differential geometry. 'r' refers to a vector created using the first helper function.

- `m(a, b, c)`: Helper function for creating 3D vectors.
- `norm(r)`: Computes the norm of a vector
- `T(r)`: Tangent vector field
- `N(r)`: Normal vector field
- `B(r)`: Binormal vector field
- `curvature(r)`: Computes the curvature of a parametric curve
- `torsion(r)`: Computes the torsion of a parametric curve
- `osculating_circle(r, a)`: Generates the osculating circle at parameter value a

## Input Format

### Vector Input
```python
m(a, b, c)  # Creates a 3D vector [x, y, z]
```

### Parametric Curves
```python
# Using the m() function:
m(cos(t), sin(t), t)  # Helix
```

### Implicit Surfaces
```python
x^2 + y^2 + z^2 - 1  # Sphere
```

### Parametric Surfaces
```python
m(u*cos(v), u*sin(v), v)  # Helicoid
```

## Constraints and Limitations

- Functions must be real-valued (complex results are filtered out)
- Parameter ranges:
  - t-range for curves: Default (0, 1)
  - u,v-ranges for surfaces: Default (0, 1)
- Bounds are automatically adjusted based on global and local settings
- Implicit multiplication is supported but should be used carefully
- Functions must be continuous within their domains

## Error Handling

The application includes robust error handling for:
- Invalid mathematical expressions
- Complex number results
- Non-real outputs
- Undefined regions
- Invalid parameter ranges
- Missing coefficients

## Implementation Details

- Uses SymPy for symbolic mathematics
- VTK for 3D rendering
- Custom parsing and transformation pipeline for mathematical expressions
- Safe evaluation system for numerical computations
- Automatic simplification and expansion of expressions

## Installation

### Using pip

1. Clone the repository:
   ```sh
   git clone https://github.com/motilin/VTK.git
   cd VTK
   ```

2. Create a virtual environment (optional but recommended):
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```sh
   pip install -r requirements.txt
   ```

### Using conda

1. Clone the repository:
   ```sh
   git clone https://github.com/motilin/VTK.git
   cd VTK
   ```

2. Create a conda environment:
   ```sh
   conda create --name vtk_env python=3.8
   conda activate vtk_env
   ```

3. Install the required packages:
   ```sh
   conda install --file requirements.txt
   ```

## Running the Application

To run the application, execute the following command:
```sh
python plot_function.py
```

## Keyboard Shortcuts

- **/**: Focus the input box
- **R**: Reset to the mathematical view
- **X**: Set to 2D view
- **J**: Rotate the scene upward
- **K**: Rotate the scene downward
- **L**: Rotate the scene clockwise
- **H**: Rotate the scene counterclockwise
- **Q**: Quit the application
- **W**: Switch to wireframe view mode (VTK native)
- **S**: Switch to surface view mode (VTK native)
- **Ctrl+Shift+P**: Show the command palette
- **Left Arrow**: Roll the view clockwise around the view direction
- **Right Arrow**: Roll the view counterclockwise around the view direction

## Saving, Loading, and Exporting

- **Save State**: Save the current state of the visualization to a JSON file.
- **Load State**: Load a previously saved state from a JSON file.
- **Export to OBJ**: Export the current view to an OBJ file.
- **Export to PNG**: Export the current view to a PNG file.
- **Export to HTML**: Export the current view to an interactive WebGL visualization.

## Project Structure

```ini
.
├── apps
│   └── plot_function.py
├── Dockerfile
├── qt
│   ├── __init_.py
│   ├── callbacks.py
│   ├── camera.py
│   ├── color_picker.py
│   ├── command_palette.py
│   ├── main_window.py
│   ├── range_slider.py
│   ├── slider.py
│   └── widgets.py
├── README.md
├── requirements.txt
└── src
    ├── core
    │   ├── __init__.py
    │   ├── constants.py
    │   ├── interactor.py
    │   └── visualization.py
    ├── __init__.py
    ├── math
    │   ├── __init__.py
    │   ├── custom_transformations.py
    │   ├── func_utils.py
    │   ├── implicit_functions.py
    │   ├── text_preprocessing.py
    │   └── tuple_parser.py
    ├── utils
    │   ├── __init__.py
    │   ├── cube_axes.py
    │   ├── line_utils.py
    │   └── surface_utils.py
    └── widgets
        ├── __init__.py
        ├── callbacks.py
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you have any suggestions or find any bugs.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Acknowledgements

This project uses the following libraries and frameworks:

- [VTK (Visualization Toolkit)](https://vtk.org/)
- [SymPy](https://www.sympy.org/)
- [NumPy](https://numpy.org/)
- [Rich](https://github.com/willmcgugan/rich)
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/intro)