from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QLineEdit, QPushButton, QLabel
from PyQt6.QtCore import Qt
from src.engine.step_engine import StepEngine

class SolverView(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = StepEngine()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("The Solver")
        header.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Chat History
        self.chat_history = QListWidget()
        self.chat_history.setObjectName("chat_history")
        layout.addWidget(self.chat_history)
        
        # Input Area
        input_layout = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setObjectName("input_field")
        self.input_field.setPlaceholderText("Escribe tu ecuación aquí (ej. y' + 2y = e^x)...")
        input_layout.addWidget(self.input_field)
        
        self.send_btn = QPushButton("Enviar")
        self.send_btn.setObjectName("send_btn")
        self.send_btn.clicked.connect(self._handle_send)
        input_layout.addWidget(self.send_btn)
        
        layout.addLayout(input_layout)

    def _handle_send(self):
        text = self.input_field.text().strip()
        if text:
            # Add User message
            self.chat_history.addItem(f"Tú: {text}")
            self.input_field.clear()
            
            # Simple heuristic to transform user input to Engine format
            # This is a basic integration for demonstration
            # In a real app, we'd need a robust parser from 'y' + 2y' to SymPy objects
            engine_input = text
            if "y'" in text:
                engine_input = text.replace("y'", "Derivative(y(x), x)").replace("e^x", "exp(x)")
                # Remove spaces and normalize multiplication for basic parsing if needed
            
            self.chat_history.addItem("Solver: ¡Entendido! Analizando...")
            
            try:
                steps = self.engine.solve_steps(engine_input)
                if steps:
                    for step in steps:
                        # Display explanation
                        self.chat_history.addItem(f"Solver: {step.explanation}")
                        # Display math (Mocking LaTeX rendering as text for now)
                        self.chat_history.addItem(f"        [ {step.latex} ]")
                else:
                    self.chat_history.addItem("Solver: No pude encontrar pasos para esta ecuación aún.")
            except Exception as e:
                self.chat_history.addItem(f"Solver: Ocurrió un error al procesar: {str(e)}")