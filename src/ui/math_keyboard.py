from PyQt6.QtWidgets import QWidget, QGridLayout, QPushButton, QLineEdit, QTextEdit
from PyQt6.QtCore import Qt, QSize

class MathKeyboard(QWidget):
    """
    A virtual keyboard widget for inserting mathematical symbols into a target input widget.
    Supports QLineEdit and QTextEdit.
    """
    def __init__(self, target_input=None, parent=None):
        super().__init__(parent)
        self.target_input = target_input
        self._setup_ui()

    def _setup_ui(self):
        layout = QGridLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        # List of symbols: (Display Label, Insertion Value)
        # Using standard unicode characters for math symbols
        symbols = [
            ('∫', '∫'),      # Integral
            ('dy/dx', 'dy/dx'), # Derivative notation
            ('∂', '∂'),      # Partial derivative
            ('∞', '∞'),      # Infinity
            ('±', '±'),      # Plus-minus
            ('√', '√'),      # Square root
            ("y'", "y'"),    # Prime notation
            ('θ', 'θ'),      # Theta
            ('λ', 'λ')       # Lambda
        ]

        # Styling for buttons
        button_style = """
            QPushButton {
                background-color: #f1f5f9;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
                color: #334155;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
                border-color: #94a3b8;
            }
            QPushButton:pressed {
                background-color: #cbd5e1;
            }
        """

        row, col = 0, 0
        max_cols = 3

        for label, value in symbols:
            btn = QPushButton(label)
            btn.setFixedSize(60, 45)
            btn.setStyleSheet(button_style)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # Connect click signal to insertion handler
            # Using lambda with default argument to capture value correctly in loop
            btn.clicked.connect(lambda checked, v=value: self._insert_symbol(v))
            
            layout.addWidget(btn, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def set_target_input(self, widget):
        """
        Sets the target input widget where symbols will be inserted.
        Accepts QLineEdit or QTextEdit.
        """
        self.target_input = widget

    def _insert_symbol(self, symbol):
        """Inserts the symbol into the target widget at the current cursor position."""
        if not self.target_input:
            return

        # Ensure widget has focus so we insert where the user expects
        self.target_input.setFocus()

        if isinstance(self.target_input, QLineEdit):
            self.target_input.insert(symbol)
        
        elif isinstance(self.target_input, QTextEdit):
            self.target_input.insertPlainText(symbol)