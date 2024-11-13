from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout


class VTKMainWindow(QMainWindow):
    def __init__(self, content):
        super().__init__()
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        self.layout.addWidget(content)
