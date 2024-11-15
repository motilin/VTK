# VTK Visualization Framework

## Overview

This project provides a framework for visualizing quadratic surfaces using VTK (Visualization Toolkit). It includes utilities for creating and managing trace lines, custom interactor styles, and slider widgets for interactive visualization. The framework is designed to be modular and extensible, making it easy to integrate into various visualization applications.

## Project Structure

```
VTK/
│
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── constants.py
│   │   ├── interactor.py
│   │   └── visualization.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── surface_utils.py
│   │   └── trace_utils.py
│   ├── math/
│   │   ├── __init__.py
│   │   └── implicit_functions.py
│   └── widgets/
│       ├── __init__.py
│       └── sliders.py
│
├── applications/
│   └── plot_function.py
│
├── qt/
│   ├── __init__.py
│   ├── main_window.py
│   ├── range_slider.py
│   └── widgets.py
│
├── README.md
├── requirements.txt
└── Dockerfile
```

### Directories and Files

- **src/**: Contains the main source code for the framework.
  - **core/**: Core functionalities such as constants, interactor styles, and visualization setup.
  - **utils/**: Utility functions for surface and trace line creation.
  - **math/**: Mathematical functions defining implicit surfaces.
  - **widgets/**: Custom slider widgets and their callbacks.
- **applications/**: Application scripts for specific visualizations.
- **qt/**: Qt-based GUI components including main window, range sliders, and widgets.
- **README.md**: Project documentation.
- **requirements.txt**: List of dependencies required to run the project.
- **Dockerfile**: Docker configuration for containerized deployment.

## Dependencies

The project requires the following Python packages:

- `vtk>=9.0.0`
- `sympy>=1.8`
- `numpy>=1.19.0`
- `rich>=10.0.0`
- `PyQt5>=5.15.0`
- `vtkmodules>=9.0.0`

You can install the dependencies using the following command:

```sh
pip install -r requirements.txt
```

## Installation using Conda

To install the package using conda, follow these steps:

1. Create a new conda environment:

    ```sh
    conda create -n vtk_env python=3.9
    ```

2. Activate the conda environment:

    ```sh
    conda activate vtk_env
    ```

3. Install the required packages:

    ```sh
    conda install -c conda-forge vtk sympy numpy rich pyqt
    ```

4. Install additional packages using pip:

    ```sh
    pip install vtkmodules
    ```

## Usage

### Main Application: Function Plotter

The main application script `applications/plot_function.py` provides an interactive interface for visualizing various implicit functions. The output includes a 3D plot of the selected function with adjustable parameters and visualization options.

To run the main application, use the following command:

```sh
python applications/plot_function.py
```

### Functions

The implicit functions used in the visualization are defined in the `src/math/implicit_functions.py` file. These functions are mathematical equations that define surfaces in 3D space. You can modify or add new functions to this file to extend the visualization capabilities.

### Key Components

- **CustomInteractorStyle**: Handles key press events for interactive visualization.
- **SliderManager**: Manages the creation and configuration of slider widgets.
- **SliderCallbacks**: Contains callback functions for slider interactions.

### Creating Custom Visualizations

You can create custom visualizations by following these steps:

1. **Setup Renderer and Window**: Use `setup_renderer` and `configure_window` functions from `src.core.visualization`.
2. **Create Actors and Mappers**: Define your VTK actors and mappers.
3. **Initialize Slider Managers**: Use `SliderManager` to create and manage sliders.
4. **Register Callbacks**: Define and register callback functions for interactive elements.

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