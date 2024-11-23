from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLineEdit,
    QListWidget,
    QFileDialog,
    QListWidgetItem,
    QShortcut,
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QKeySequence, QIcon
from src.core.interactor import export_to_obj, export_to_png, save_state, load_state
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main_window import VTKMainWindow


class CommandPalette(QDialog):
    def __init__(self, parent: "VTKMainWindow"):
        super().__init__(parent, Qt.Popup | Qt.FramelessWindowHint)
        self.parent = parent
        self.init_ui()
        self.setup_commands()

    def init_ui(self):
        # Set up the main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # Create and style the search box
        self.search_box = QLineEdit(self)
        self.search_box.setPlaceholderText("Type a command...")
        self.search_box.textChanged.connect(self.filter_commands)
        self.search_box.setStyleSheet(
            """
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background: white;
                font-size: 14px;
            }
        """
        )

        # Create and style the command list
        self.command_list = QListWidget(self)
        self.command_list.setStyleSheet(
            """
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                background: white;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 8px;
            }
            QListWidget::item:selected {
                background: #0078d4;
                color: white;
            }
            QListWidget::item:hover {
                background: #f0f0f0;
            }
        """
        )
        self.command_list.itemClicked.connect(self.handle_command)

        # Add widgets to layout
        layout.addWidget(self.search_box)
        layout.addWidget(self.command_list)

        # Set dialog size
        self.resize(400, 300)

    def setup_commands(self):
        self.commands = [
            {"text": "Load File", "action": self.load_file},
            {"text": "Save File", "action": self.save_file},
            {"text": "Export PNG", "action": self.export_as_png},
            {"text": "Export OBJ", "action": self.export_as_obj},
        ]

        for cmd in self.commands:
            item = QListWidgetItem(cmd["text"])
            item.setData(Qt.UserRole, cmd["action"])
            self.command_list.addItem(item)

    def filter_commands(self, text):
        for i in range(self.command_list.count()):
            item = self.command_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def handle_command(self, item):
        action = item.data(Qt.UserRole)
        self.close()
        action()

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self.parent, "Load State", "", "JSON Files (*.json)"
        )
        if file_path:
            self.load_state(file_path)

    def save_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self.parent, "Save State", "", "JSON Files (*.json)"
        )
        if file_path:
            self.save_state(file_path)

    def export_as_png(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self.parent, "Export PNG", "", "PNG Files (*.png)"
        )
        if file_path:
            self.export_png(file_path)

    def export_as_obj(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self.parent, "Export OBJ", "", "OBJ Files (*.obj)"
        )
        if file_path:
            self.export_obj(file_path)

    def showEvent(self, event):
        # Center the palette relative to the parent window
        if self.parent:
            parent_rect = self.parent.geometry()
            x = parent_rect.center().x() - self.width() // 2
            y = parent_rect.center().y() - self.height() // 2
            self.move(x, y)
        super().showEvent(event)
        self.search_box.setFocus()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() in (Qt.Key_Enter, Qt.Key_Return):
            if self.command_list.currentItem():
                self.handle_command(self.command_list.currentItem())
        elif event.key() == Qt.Key_Up:
            current_row = self.command_list.currentRow()
            if current_row > 0:
                self.command_list.setCurrentRow(current_row - 1)
        elif event.key() == Qt.Key_Down:
            current_row = self.command_list.currentRow()
            if current_row < self.command_list.count() - 1:
                self.command_list.setCurrentRow(current_row + 1)
        else:
            super().keyPressEvent(event)

    def save_state(self, filepath):
        save_state(self.parent.widget, filepath)

    def load_state(self, filepath):
        load_state(self.parent.widget, filepath)

    def export_png(self, filepath):
        export_to_png(self.parent.widget.vtk_widget, filepath)

    def export_obj(self, filepath):
        export_to_obj(self.parent.widget.vtk_widget, filepath)
