# VTK Visualization Framework

## Overview

This project provides a framework for visualizing quadratic surfaces using VTK (Visualization Toolkit). It includes utilities for creating and managing trace lines, custom interactor styles, and slider widgets for interactive visualization. The framework is designed to be modular and extensible, making it easy to integrate into various visualization applications.

## Project Structure

```
quadratic_surface/
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
│   └── widgets/
│       ├── __init__.py
│       └── sliders.py
│
├── examples/
│   └── cylinder_example.py
│
├── README.md
└── requirements.txt

```

### Directories and Files

- **src/**: Contains the main source code for the framework.
  - **core/**: Core functionalities such as constants, interactor styles, and visualization setup.
  - **utils/**: Utility functions for surface and trace line creation.
  - **widgets/**: Custom slider widgets and their callbacks.
- **examples/**: Example scripts demonstrating how to use the framework.
- **README.md**: Project documentation.
- **requirements.txt**: List of dependencies required to run the project.

## Dependencies

The project requires the following Python packages:

- `vtk>=9.0.0`
- `sympy>=1.8`
- `numpy>=1.19.0`
- `rich>=10.0.0`

You can install the dependencies using the following command:

```sh
pip install -r requirements.txt

```

## Usage

### Example: Cylinder Visualization

The `applications/cylinder_example.py` script demonstrates how to use the framework to visualize a cylinder with interactive sliders for color, resolution, and height/width ratio.

To run the example, use the following command:

```sh
python applications/cylinder_example.py
```

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
```
