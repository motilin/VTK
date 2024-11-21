from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QSizePolicy,
    QLabel,
    QComboBox,
    QHBoxLayout,
    QSlider,
    QCheckBox,
    QLineEdit,
    QTextEdit,
    QColorDialog,
)
from PyQt5.QtGui import QDoubleValidator, QFontMetrics, QColor
from PyQt5.QtCore import Qt
import vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from src.core.interactor import CustomInteractorStyle
from qt.range_slider import RangeSlider, add_range_sliders
from src.core.constants import CONTROL_PANEL_WIDTH, CONTROL_PANEL_SPACING, SCALE_FACTOR, COLORS
from qt.color_picker import ColorPicker


class VTKWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.intereactor = QVTKRenderWindowInteractor(self)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.intereactor)
        self.setLayout(self.layout)
        self.input_box = None

        self.renderer = vtk.vtkRenderer()
        self.intereactor.GetRenderWindow().AddRenderer(self.renderer)
        self.interactor = self.intereactor.GetRenderWindow().GetInteractor()

        style = CustomInteractorStyle(self)
        self.interactor.SetInteractorStyle(style)

    def get_render_window(self):
        return self.intereactor.GetRenderWindow()


class ControlWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.layout.setSpacing(CONTROL_PANEL_SPACING)
        self.layout.setAlignment(Qt.AlignTop | Qt.AlignRight)
        self.setLayout(self.layout)
        self.setFixedWidth(CONTROL_PANEL_WIDTH)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

    def add_label(self, text):
        label = QLabel(text, self)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.layout.addWidget(label)
        return label

    def add_slider(self, bounds, value, text, update_callback):
        label = QLabel(text, self)
        label.setSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Fixed
        )  # Prevent label from expanding

        # Create and configure slider
        slider = QSlider(Qt.Horizontal, self)
        slider.setMinimum(int(bounds[0] * SCALE_FACTOR))
        slider.setMaximum(int(bounds[1] * SCALE_FACTOR))
        slider.setValue(int(value * SCALE_FACTOR))
        slider.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed
        )  # Make slider expand horizontally

        # Create and configure text box
        text_box = QLineEdit(self)
        text_box.setText(f"{value:.2f}")
        text_box.setAlignment(Qt.AlignRight)
        text_box.setFixedWidth(50)  # Width enough for "00.00"
        text_box.setValidator(
            QDoubleValidator(bounds[0], bounds[1], 2)
        )  # Allow only valid numbers

        # Function to update the text box when slider moves
        def update_text_from_slider(value):
            scaled_value = value / SCALE_FACTOR
            text_box.setText(f"{scaled_value:.2f}")
            update_callback(scaled_value)

        # Function to update the slider when text changes
        def update_slider_from_text():
            try:
                new_value = float(text_box.text())
                if bounds[0] <= new_value <= bounds[1]:
                    slider.setValue(int(new_value * SCALE_FACTOR))
                    update_callback(new_value)
            except ValueError:
                # Restore previous valid value if input is invalid
                scaled_value = slider.value() / SCALE_FACTOR
                text_box.setText(f"{scaled_value:.2f}")

        # Connect signals
        slider.valueChanged.connect(update_text_from_slider)
        text_box.returnPressed.connect(update_slider_from_text)

        # Create layout
        slider_layout = QHBoxLayout()
        slider_layout.setSpacing(5)  # Small spacing between elements
        slider_layout.addWidget(label)
        slider_layout.addWidget(
            slider, stretch=1
        )  # Add stretch factor to make slider expand
        slider_layout.addWidget(text_box)
        slider_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins

        self.layout.addLayout(slider_layout)
        
        return slider

    def add_range_sliders(self, bounds, update_callback):
        add_range_sliders(
            self,
            bounds,
            self.layout,
            update_callback,
        )
        
    def add_range_text_boxes(self, text, bounds, update_callback):
        label = QLabel(text, self)
        label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        label.setAlignment(Qt.AlignLeft)
        min_text_box = QLineEdit(self)
        min_text_box.setAlignment(Qt.AlignRight)
        min_text_box.setFixedWidth(70)  # width enough for "-0000.00"
        min_text_box.setText(str(bounds[0]))
        max_text_box = QLineEdit(self)
        max_text_box.setAlignment(Qt.AlignRight)
        max_text_box.setFixedWidth(70)  # width enough for "-0000.00"
        max_text_box.setText(str(bounds[1]))

        # Function to send new range to update_callback
        def update_range():
            try:
                x_min = float(min_text_box.text())
                x_max = float(max_text_box.text())
                if x_min <= x_max:
                    update_callback((x_min, x_max))
            except ValueError:
                pass

        # Connect signals
        min_text_box.returnPressed.connect(update_range)
        max_text_box.returnPressed.connect(update_range)

        # Create layout
        range_layout = QHBoxLayout()
        range_layout.setSpacing(10)
        range_layout.addWidget(label, alignment=Qt.AlignLeft)
        range_layout.addWidget(min_text_box)
        range_layout.addWidget(max_text_box)
        range_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addLayout(range_layout)
        
        return min_text_box, max_text_box

    def add_button(self, text, callback):
        button = QPushButton(text, self)
        button.clicked.connect(callback)
        button_layout = QHBoxLayout()
        button_layout.addWidget(button, alignment=Qt.AlignTop)
        self.layout.addLayout(button_layout)
        
        return button

    def add_dropdown(self, text, options, callback):
        label = QLabel(text, self)
        dropdown = QComboBox(self)
        dropdown.addItems(options)
        dropdown.currentIndexChanged.connect(callback)

        # Ensure dropdown stretches
        dropdown.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        dropdown_layout = QHBoxLayout()
        dropdown_layout.addWidget(label, alignment=Qt.AlignLeft)
        dropdown_layout.addWidget(dropdown, stretch=1)

        # Set the layout stretch factor for proper resizing
        dropdown_layout.setStretch(0, 0)  # Label doesn't stretch
        dropdown_layout.setStretch(1, 1)  # Dropdown stretches

        self.layout.addLayout(dropdown_layout)
        
        return dropdown

    def update_dropdown(self, dropdown, options):
        dropdown.clear()
        dropdown.addItems(options)

    def add_checkbox(self, text, value, callback):
        checkbox = QCheckBox(text, self)
        checkbox.stateChanged.connect(callback)
        checkbox.setChecked(value)
        checkbox_layout = QHBoxLayout()
        checkbox_layout.addWidget(checkbox, alignment=Qt.AlignTop)
        self.layout.addLayout(checkbox_layout)
        
        return checkbox

    def add_textbox(self, text, callback):
        label = QLabel(text, self)
        button = QPushButton("Draw", self)
        textbox = QTextEdit(self)
        textbox.setFixedWidth(CONTROL_PANEL_WIDTH - 20)
        font_metrics = QFontMetrics(textbox.font())
        line_height = font_metrics.lineSpacing()
        textbox.setFixedHeight(line_height * 2)

        def adjust_textbox_height():
            text = textbox.toPlainText()
            lines = text.count("\n") + 2
            textbox.setFixedHeight(line_height * max(lines, 2))

        textbox.textChanged.connect(adjust_textbox_height)
        button.clicked.connect(lambda: callback(textbox.toPlainText()))

        # Use an event filter to handle Ctrl+Enter
        textbox.installEventFilter(self)

        # Save button and textbox for use in the event filter
        self.active_button = button
        self.active_textbox = textbox

        textbox_layout = QVBoxLayout()
        textbox_layout.addWidget(label, alignment=Qt.AlignTop)
        textbox_layout.addWidget(textbox, alignment=Qt.AlignTop)
        textbox_layout.addWidget(button, alignment=Qt.AlignTop)
        self.layout.addLayout(textbox_layout)
       
        self.input_box = textbox 
        return textbox


    def eventFilter(self, obj, event):
        if obj == self.active_textbox and event.type() == event.KeyPress:
            if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
                if event.modifiers() & Qt.ControlModifier:  # Check for Ctrl modifier
                    self.active_button.click()
                    return True  # Consume the event
            if event.key() == Qt.Key_Escape:
                self.active_textbox.clearFocus()
                return True
        return super().eventFilter(obj, event)

    def remove_layout_by_label(self, label_text):
        for i in reversed(range(self.layout.count())):
            item = self.layout.itemAt(i)
            if isinstance(item, QHBoxLayout):
                for j in range(item.count()):
                    widget = item.itemAt(j).widget()
                    if isinstance(widget, QLabel) and widget.text() == label_text:
                        # Remove all widgets in the QHBoxLayout
                        while item.count():
                            widget_to_remove = item.takeAt(0).widget()
                            if widget_to_remove:
                                widget_to_remove.deleteLater()
                        # Remove the QHBoxLayout itself
                        self.layout.removeItem(item)
                        break
                    
    def add_color_picker(self, text, color, callback, dual=False):
        color_picker = ColorPicker(self, text, color, callback, dual)
        self.layout.addLayout(color_picker.layout)
        return color_picker 