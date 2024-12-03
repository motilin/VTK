from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QStyledItemDelegate
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QTextDocument, QFontMetrics


class CustomLatexWidget(QWidget):
    def __init__(self, latex_text, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.web_view = QWebEngineView(self)
        self.layout.addWidget(self.web_view)
        self.setLayout(self.layout)
        self.set_latex_text(latex_text)

    def set_latex_text(self, latex_text):
        html_content = f"""
        <html>
        <head>
            <script type="text/javascript" async
              src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML">
            </script>
        </head>
        <body>
            <p>$$ {latex_text} $$</p>
        </body>
        </html>
        """
        self.web_view.setHtml(html_content)


class LatexDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        latex_text = index.data()
        editor = CustomLatexWidget(latex_text, parent)
        return editor

    def setEditorData(self, editor, index):
        latex_text = index.data()
        editor.set_latex_text(latex_text)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def sizeHint(self, option, index):
        latex_text = index.data()
        font_metrics = QFontMetrics(option.font)
        text_width = font_metrics.width(latex_text)
        return QSize(text_width + 20, 30)  # Adjust width padding as needed
