from PyQt5.QtWidgets import (
    QLabel,
    QSlider,
    QLineEdit,
    QHBoxLayout,
    QDialog,
    QVBoxLayout,
    QWidget,
    QSizePolicy,
    QGraphicsDropShadowEffect,
)
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QFont, QDoubleValidator, QColor

from src.core.constants import SCALE_FACTOR, DEFAULT_SLIDER_BOUNDS
import re

class Slider(QWidget):
    def __init__(self, parent, bounds, value, text, update_callback):
        super().__init__(parent)

        if not bounds:
            bounds = DEFAULT_SLIDER_BOUNDS

        self.bounds = bounds
        self.update_callback = update_callback

        # Use a vertical layout to stack the label, slider, and text box
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)  # Remove margins

        # Create layout
        self.slider_layout = QHBoxLayout()
        self.slider_layout.setSpacing(5)  # Small spacing between elements
        self.slider_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins

        # Create label
        self.label = QLabel(text, self)
        self.label.setSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Fixed
        )  # Prevent label from expanding

        # Create and configure slider
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed
        )  # Make slider expand horizontally

        # Create and configure text box
        self.text_box = QLineEdit(self)
        self.text_box.setAlignment(Qt.AlignRight)
        self.text_box.setFixedWidth(50)  # Width enough for "00.00"

        # Setup initial state
        self._setup_slider(bounds, value)

        # Bounds modification dialog
        def show_bounds_dialog():
            dialog = BoundsDialog(text, self.bounds[0], self.bounds[1], self)

            # Position dialog near the label
            dialog_pos = self.label.mapToGlobal(self.label.rect().bottomLeft())
            dialog.move(dialog_pos)

            if dialog.exec_() == QDialog.Accepted:
                new_bounds = dialog.get_bounds()

                # Validate and update bounds
                if new_bounds[0] < new_bounds[1]:
                    if self.text_box.text() != "":
                        value = float(self.text_box.text())
                        self.set_value(value, (new_bounds))
                        self.update_callback(value, self.bounds)

        # Connect label click event to bounds dialog
        self.label.mousePressEvent = lambda event: show_bounds_dialog()

        # Add widgets to layout
        self.slider_layout.addWidget(self.label)
        self.slider_layout.addWidget(self.slider, stretch=1)
        self.slider_layout.addWidget(self.text_box)

        self.layout.addLayout(self.slider_layout)

    def _setup_slider(self, bounds, value):
        """Initial setup of slider, text box, and connections"""
        # Set slider bounds
        self.slider.setMinimum(int(bounds[0] * SCALE_FACTOR))
        self.slider.setMaximum(int(bounds[1] * SCALE_FACTOR))

        # Set validator
        # self.text_box.setValidator(QDoubleValidator(bounds[0], bounds[1], 2))
        self.text_box.setValidator(CustomDoubleValidator(bounds[0], bounds[1], 2))

        # Function to update the text box when slider moves
        def update_text_from_slider(slider_value):
            scaled_value = slider_value / SCALE_FACTOR
            self.text_box.setText(f"{scaled_value:.2f}")
            self.update_callback(scaled_value, self.bounds)

        # Function to update the slider when text changes
        def update_slider_from_text():
            try:
                new_value = float(self.text_box.text())
                if bounds[0] <= new_value <= bounds[1]:
                    self.slider.setValue(int(new_value * SCALE_FACTOR))
                    self.update_callback(new_value, self.bounds)
            except ValueError:
                # Restore previous valid value if input is invalid
                scaled_value = self.slider.value() / SCALE_FACTOR
                self.text_box.setText(f"{scaled_value:.2f}")

        # Connect signals
        self.slider.valueChanged.connect(update_text_from_slider)
        self.text_box.returnPressed.connect(update_slider_from_text)

        # Set initial value
        self.slider.setValue(int(value * SCALE_FACTOR))
        self.text_box.setText(f"{value:.2f}")

    def set_value(self, value, bounds=None):
        """
        Programmatically set slider value and optionally update bounds

        :param value: New value for the slider
        :param min_bound: New minimum bound (optional)
        :param max_bound: New maximum bound (optional)
        """

        if not bounds:
            min_bound, max_bound = self.bounds
        else:
            min_bound, max_bound = bounds

        # Update bounds if provided
        if min_bound is not None and max_bound is not None:
            if min_bound > max_bound:
                raise ValueError("Minimum bound must be less than maximum bound")

            # Update bounds
            self.slider.setMinimum(int(min_bound * SCALE_FACTOR))
            self.slider.setMaximum(int(max_bound * SCALE_FACTOR))

            # Update text box validator
            # self.text_box.setValidator(QDoubleValidator(min_bound, max_bound, 2))
            self.text_box.setValidator(CustomDoubleValidator(min_bound, max_bound, 2))

            # Update stored bounds
            self.bounds = (min_bound, max_bound)
        else:
            # Use existing bounds if not provided
            min_bound, max_bound = self.bounds

        # Clamp value to new/existing bounds
        clamped_value = max(min_bound, min(value, max_bound))

        # Set slider and text box
        self.slider.setValue(int(clamped_value * SCALE_FACTOR))
        self.text_box.setText(f"{clamped_value:.2f}")

        # Call update callback
        self.update_callback(clamped_value, self.bounds)


class BoundsDialog(QDialog):
    def __init__(self, label_text, current_min, current_max, parent=None):
        super().__init__(parent, Qt.FramelessWindowHint | Qt.Popup)

        # Style for a modern, floating panel look
        self.setStyleSheet(
            """
            QDialog {
                background-color: white;
                border-radius: 8px;
                padding: 10px;
            }
            QLineEdit {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 5px;
            }
        """
        )

        # Add shadow effect for a floating panel look
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.setGraphicsEffect(shadow)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # Min bound input
        self.min_input = QLineEdit(str(current_min))
        self.min_input.setFixedWidth(70)
        self.min_input.setAlignment(Qt.AlignLeft)
        self.min_input.setValidator(QDoubleValidator())

        # Label between inputs
        label_between = QLabel(f"< {label_text} <")
        label_between.setAlignment(Qt.AlignLeft)
        label_between.setAlignment(Qt.AlignVCenter)
        label_font = QFont()
        label_font.setItalic(True)
        label_between.setFont(label_font)

        # Max bound input
        self.max_input = QLineEdit(str(current_max))
        self.max_input.setValidator(QDoubleValidator())
        self.max_input.setFixedWidth(70)
        self.max_input.setAlignment(Qt.AlignLeft)

        layout.addWidget(self.min_input, alignment=Qt.AlignLeft)
        layout.addWidget(label_between, alignment=Qt.AlignHCenter)
        layout.addWidget(self.max_input, alignment=Qt.AlignRight)

        self.setLayout(layout)

        # Enter key press handler
        self.min_input.returnPressed.connect(self.accept)
        self.max_input.returnPressed.connect(self.accept)

    def get_bounds(self):
        return (float(self.min_input.text()), float(self.max_input.text()))



class CustomDoubleValidator(QDoubleValidator):
    def __init__(self, bottom, top, decimals, parent=None):
        super().__init__(bottom, top, decimals, parent)
        self.bottom = bottom
        self.top = top
        self.decimals = decimals

    def validate(self, input_text, pos):
        # Allow empty input
        if not input_text:
            return QDoubleValidator.Intermediate, input_text, pos

        # Allow '-' or '-.' as an intermediate state
        if input_text == '-' or input_text == '-.':
            return QDoubleValidator.Intermediate, input_text, pos

        # Remove leading/trailing whitespace
        input_text = input_text.strip()

        # More permissive regex to handle various number formats
        pattern = r"^[+-]?(\d*\.?\d*|\.\d+)$"
        if not re.match(pattern, input_text):
            return QDoubleValidator.Intermediate, input_text, pos

        # Try to convert to float
        try:
            value = float(input_text)
        except ValueError:
            return QDoubleValidator.Invalid, input_text, pos

        # Check range
        if self.bottom is not None and self.top is not None:
            if value < self.bottom or value > self.top:
                return QDoubleValidator.Intermediate, input_text, pos

        # Check decimal places
        if "." in input_text:
            decimal_part = input_text.split(".")[1]
            if len(decimal_part) > self.decimals:
                return QDoubleValidator.Invalid, input_text, pos

        return QDoubleValidator.Acceptable, input_text, pos