from PyQt5.QtWidgets import (
    QLabel,
    QLineEdit,
    QHBoxLayout,
    QWidget,
    QSpacerItem,
    QSizePolicy,
)
from PyQt5.QtCore import Qt, pyqtSignal, QRectF, QEvent, QSize
from PyQt5.QtGui import QFont, QDoubleValidator, QColor, QPainter, QBrush, QPen

from qt.slider import BoundsDialog
from src.core.constants import SCALE_FACTOR, DEFAULT_SLIDER_BOUNDS

LABEL_SLIDER_SPACING = 10
SLIDER_INPUT_SPACING = 10
MIN_MAX_INPUT_SPACING = 5

class RangeSlider(QWidget):
    lowerValueChanged = pyqtSignal(float)
    upperValueChanged = pyqtSignal(float)
    rangeChanged = pyqtSignal(float, float)

    def __init__(self, parent, bounds, values, text, update_callback):
        super().__init__(parent)
        self.bounds = bounds
        self.values = values
        self.text = text
        self.update_callback = update_callback

        self.mMinimum, self.mMaximum = bounds
        self.mLowerValue, self.mUpperValue = values
        self.mFirstHandlePressed = False
        self.mSecondHandlePressed = False
        self.mInterval = self.mMaximum - self.mMinimum
        self.mBackgroudColorEnabled = QColor(0x1E, 0x90, 0xFF)
        self.mBackgroudColorDisabled = Qt.darkGray
        self.mBackgroudColor = self.mBackgroudColorEnabled
        self.orientation = Qt.Horizontal

        self.setMouseTracking(True)

        # Create layout with precise spacing
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)  # Set to 0 to control spacing manually

        # Create label with right margin
        self.label = QLabel(self.text)
        self.label.setAlignment(Qt.AlignLeft)
        self.label.setAlignment(Qt.AlignVCenter)
        self.label.setFont(QFont("Arial", 10))
        self.label.setMinimumWidth(20)
        self.label.setMargin(1)  # Add margin to label
        self.label.mousePressEvent = self.open_bounds_dialog
        self.layout.addWidget(self.label)

        # Create slider widget
        self.slider_widget = QWidget(self)
        self.slider_layout = QHBoxLayout(self.slider_widget)
        self.slider_layout.setContentsMargins(0, 0, 0, 0)
        self.slider_layout.setSpacing(0)
        self.layout.addWidget(self.slider_widget, 1)

        # Create min and max value textboxes
        self.min_input = QLineEdit(f"{self.mLowerValue:.2f}")
        self.min_input.setFixedWidth(50)
        self.min_input.setValidator(QDoubleValidator(self.mMinimum, self.mMaximum, 2))
        self.min_input.editingFinished.connect(self.update_min_value)
        self.layout.addWidget(self.min_input)
        
        min_max_input_spacer = QSpacerItem(MIN_MAX_INPUT_SPACING, 0, QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.layout.addItem(min_max_input_spacer)

        self.max_input = QLineEdit(f"{self.mUpperValue:.2f}")
        self.max_input.setFixedWidth(50)
        self.max_input.setValidator(QDoubleValidator(self.mMinimum, self.mMaximum, 2))
        self.max_input.editingFinished.connect(self.update_max_value)
        self.layout.addWidget(self.max_input)

        # Add spacer to stretch the slider bar
        self.layout.addItem(
            QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )

        # Initial callback trigger
        self.update_callback(
            (self.mLowerValue, self.mUpperValue), (self.mMinimum, self.mMaximum)
        )

    def paintEvent(self, event):
        painter = QPainter(self)

        # Calculate the actual space available for the slider
        sliderStart = self.label.width()  # Add spacing after label
        sliderWidth = (self.width() 
                      - sliderStart  # Start position
                      - self.min_input.width()  # Width of min input
                      - self.max_input.width()  # Width of max input
                      - SLIDER_INPUT_SPACING  # Spacing before min input (matches your spacer)
                      - MIN_MAX_INPUT_SPACING)  # Spacing between inputs

        # Background
        backgroundRect = QRectF(
            sliderStart,
            (self.height() - 5) / 2,
            sliderWidth,
            5,
        )
        pen = QPen(Qt.gray, 1)
        painter.setPen(pen)
        painter.setRenderHint(QPainter.Antialiasing)
        backgroundBrush = QBrush(QColor(0xD0, 0xD0, 0xD0))
        painter.setBrush(backgroundBrush)
        painter.drawRoundedRect(backgroundRect, 1, 1)

        # First value handle rect
        pen.setColor(Qt.darkGray)
        pen.setWidth(1)
        painter.setPen(pen)
        handleBrush = QBrush(QColor(0xFA, 0xFA, 0xFA))
        painter.setBrush(handleBrush)
        leftHandleRect = self.firstHandleRect()
        painter.drawRoundedRect(leftHandleRect, 2, 2)

        # Second value handle rect
        rightHandleRect = self.secondHandleRect()
        painter.drawRoundedRect(rightHandleRect, 2, 2)

        # Handles
        painter.setRenderHint(QPainter.Antialiasing, False)
        selectedRect = backgroundRect
        selectedRect.setLeft(leftHandleRect.right() + 0.5)
        selectedRect.setRight(rightHandleRect.left() - 0.5)
        selectedBrush = QBrush(self.mBackgroudColor)
        painter.setBrush(selectedBrush)
        painter.drawRect(selectedRect)

    def firstHandleRect(self):
        percentage = (self.mLowerValue - self.mMinimum) / self.mInterval
        return self.handleRect(percentage * self.validLength() + self.label.width())

    def secondHandleRect(self):
        percentage = (self.mUpperValue - self.mMinimum) / self.mInterval
        return self.handleRect(percentage * self.validLength() + self.label.width())

    def handleRect(self, value):
        return QRectF(value, (self.height() - 11) / 2, 11, 11)

    def mousePressEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            posValue = event.pos().x()

            # Adjust for handle's center
            firstHandleRect = self.firstHandleRect()
            secondHandleRect = self.secondHandleRect()

            # Expand hit areas for more precise clicking
            expanded_first_handle = firstHandleRect.adjusted(-5, -5, 5, 5)
            expanded_second_handle = secondHandleRect.adjusted(-5, -5, 5, 5)

            self.mSecondHandlePressed = expanded_second_handle.contains(event.pos())
            self.mFirstHandlePressed = (
                not self.mSecondHandlePressed
                and expanded_first_handle.contains(event.pos())
            )

            if self.mFirstHandlePressed:
                self.mDelta = posValue - (firstHandleRect.center().x())
            elif self.mSecondHandlePressed:
                self.mDelta = posValue - (secondHandleRect.center().x())

            if 2 <= event.pos().y() <= self.height() - 2:
                step = max(self.mInterval / 10, 0.01)
                if posValue < firstHandleRect.center().x():
                    self.setLowerValue(self.mLowerValue - step)
                elif (
                    firstHandleRect.center().x()
                    < posValue
                    < secondHandleRect.center().x()
                ):
                    midpoint = (
                        firstHandleRect.center().x() + secondHandleRect.center().x()
                    ) / 2
                    if posValue < midpoint:
                        self.setLowerValue(
                            min(self.mLowerValue + step, self.mUpperValue)
                        )
                    else:
                        self.setUpperValue(
                            max(self.mUpperValue - step, self.mLowerValue)
                        )
                elif posValue > secondHandleRect.center().x():
                    self.setUpperValue(self.mUpperValue + step)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            posValue = event.pos().x()

            if self.mFirstHandlePressed:
                new_lower_value = (
                    posValue - self.mDelta - self.label.width()
                ) / self.validLength() * self.mInterval + self.mMinimum
                if new_lower_value <= self.mUpperValue:
                    self.setLowerValue(new_lower_value)
            elif self.mSecondHandlePressed:
                new_upper_value = (
                    posValue - self.mDelta - self.label.width()
                ) / self.validLength() * self.mInterval + self.mMinimum
                if new_upper_value >= self.mLowerValue:
                    self.setUpperValue(new_upper_value)

    def mouseReleaseEvent(self, event):
        self.mFirstHandlePressed = False
        self.mSecondHandlePressed = False

    def setLowerValue(self, value):
        value = max(min(value, self.mMaximum), self.mMinimum)
        if value != self.mLowerValue:
            self.mLowerValue = value
            self.min_input.setText(f"{self.mLowerValue:.2f}")
            self.lowerValueChanged.emit(self.mLowerValue)
            self.update()
            # Trigger callback with full range info
            self.update_callback(
                (self.mLowerValue, self.mUpperValue), (self.mMinimum, self.mMaximum)
            )

    def setUpperValue(self, value):
        value = max(min(value, self.mMaximum), self.mMinimum)
        if value != self.mUpperValue:
            self.mUpperValue = value
            self.max_input.setText(f"{self.mUpperValue:.2f}")
            self.upperValueChanged.emit(self.mUpperValue)
            self.update()
            # Trigger callback with full range info
            self.update_callback(
                (self.mLowerValue, self.mUpperValue), (self.mMinimum, self.mMaximum)
            )

    def setMinimum(self, value):
        if value < self.mMaximum:
            self.mMinimum = value
            self.mInterval = self.mMaximum - self.mMinimum

            # Adjust current values if they're out of new bounds
            self.mLowerValue = max(self.mLowerValue, self.mMinimum)
            self.mUpperValue = max(self.mUpperValue, self.mMinimum)

            self.min_input.setText(f"{self.mLowerValue:.2f}")
            self.max_input.setText(f"{self.mUpperValue:.2f}")

            self.update()
            self.rangeChanged.emit(self.mMinimum, self.mMaximum)

            # Trigger callback with updated range
            self.update_callback(
                (self.mLowerValue, self.mUpperValue), (self.mMinimum, self.mMaximum)
            )

    def setMaximum(self, value):
        if value > self.mMinimum:
            self.mMaximum = value
            self.mInterval = self.mMaximum - self.mMinimum

            # Adjust current values if they're out of new bounds
            self.mLowerValue = min(self.mLowerValue, self.mMaximum)
            self.mUpperValue = min(self.mUpperValue, self.mMaximum)

            self.min_input.setText(f"{self.mLowerValue:.2f}")
            self.max_input.setText(f"{self.mUpperValue:.2f}")

            self.update()
            self.rangeChanged.emit(self.mMinimum, self.mMaximum)

            # Trigger callback with updated range
            self.update_callback(
                (self.mLowerValue, self.mUpperValue), (self.mMinimum, self.mMaximum)
            )

    def validLength(self):
        # Update to match the calculation in paintEvent
        return (self.width() 
                - self.label.width() 
                - LABEL_SLIDER_SPACING  # Label spacing
                - self.min_input.width() 
                - self.max_input.width() 
                - SLIDER_INPUT_SPACING # Spacing before min input
                - MIN_MAX_INPUT_SPACING)  # Spacing between inputs

    def update_min_value(self):
        try:
            value = float(self.min_input.text())
            self.setLowerValue(value)
        except ValueError:
            # Revert to previous value if invalid input
            self.min_input.setText(f"{self.mLowerValue:.2f}")

    def update_max_value(self):
        try:
            value = float(self.max_input.text())
            self.setUpperValue(value)
        except ValueError:
            # Revert to previous value if invalid input
            self.max_input.setText(f"{self.mUpperValue:.2f}")

    def open_bounds_dialog(self, event):
        # Position the dialog relative to the label
        dialog = BoundsDialog(self.text, self.mMinimum, self.mMaximum, self)
        global_pos = self.label.mapToGlobal(self.label.rect().bottomLeft())
        dialog.move(global_pos)

        if dialog.exec_():
            new_min, new_max = dialog.get_bounds()
            # Update bounds while maintaining current values
            self.setMinimum(new_min)
            self.setMaximum(new_max)
