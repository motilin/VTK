import sys
from PyQt5.QtWidgets import (QApplication, QComboBox, QStyledItemDelegate, QWidget, 
                             QVBoxLayout, QStyle, QProxyStyle)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFontMetrics

class WidthEnforcingStyle(QProxyStyle):
    def sizeFromContents(self, type, option, size, widget):
        s = super().sizeFromContents(type, option, size, widget)
        if type == QStyle.CT_ComboBox and widget and hasattr(widget, 'calculateMinimumWidth'):
            s.setWidth(widget.calculateMinimumWidth())
        return s

class LatexWebView(QWebEngineView):
    def __init__(self, latex_text, parent=None):
        super().__init__(parent)
        self.render_latex(latex_text)
        self.setMinimumSize(300, 50)

    def render_latex(self, latex_text):
        html_content = f"""
        <html>
        <head>
            <script type="text/x-mathjax-config">
            MathJax.Hub.Config({{
                tex2jax: {{
                    inlineMath: [['$','$'], ['\\(','\\)']],
                    displayMath: [['$$','$$'], ['\\[','\\]']],
                    processEscapes: true
                }},
                "HTML-CSS": {{ 
                    scale: 150,
                    availableFonts: ["TeX"],
                    webFont: "TeX"
                }}
            }});
            </script>
            <script type="text/javascript" async
                src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML">
            </script>
            <style>
                body {{ 
                    margin: 0; 
                    padding: 10px; 
                    display: flex; 
                    justify-content: center; 
                    align-items: center; 
                    height: 100vh;
                    font-size: 18px;
                }}
                .latex-container {{ 
                    text-align: center;
                    width: 100%;
                }}
            </style>
        </head>
        <body>
            <div class="latex-container">
                $${latex_text}$$
            </div>
        </body>
        </html>
        """
        self.setHtml(html_content)

class LatexDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        latex_text = index.data()
        return LatexWebView(latex_text, parent)
    
    def sizeHint(self, option, index):
        return QSize(300, 30)

class LatexComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setItemDelegate(LatexDelegate(self))
        
        # Custom style to enforce width
        self.setStyle(WidthEnforcingStyle())
        
        # Method to calculate minimum width
        self.calculateMinimumWidth = self._calculate_minimum_width
        
        # Ensure dropdown is wide enough
        self.setStyleSheet("""
            QComboBox QAbstractItemView {
                min-width: 300px;
            }
        """)
    
    def _calculate_minimum_width(self):
        # Calculate width based on content
        font_metrics = QFontMetrics(self.font())
        max_width = max(
            font_metrics.width(self.itemText(i)) for i in range(self.count())
        )
        return max(max_width + 50, 300)  # Minimum 300, add padding

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    combo = LatexComboBox()
    combo.addItem(r'E = mc^2')
    combo.addItem(r'\int_{-\infty}^{\infty} e^{-x^2} dx')
    combo.addItem(r'\nabla \times \vec{E} = -\frac{1}{c} \frac{\partial \vec{B}}{\partial t}')
    
    combo.show()
    sys.exit(app.exec_())