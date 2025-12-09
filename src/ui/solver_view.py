from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QLineEdit, 
    QPushButton, QLabel, QScrollArea, QFrame, QSplitter,
    QListWidgetItem, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from src.engine.step_engine import StepEngine
from src.ui.math_keyboard import MathKeyboard, MathRenderWidget


class SolutionStepWidget(QFrame):
    """Widget para mostrar un paso de solución con renderizado matemático."""
    
    def __init__(self, step_number: int, explanation: str, latex: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                margin: 4px 0;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)
        
        # Encabezado del paso
        header = QLabel(f"Paso {step_number}")
        header.setStyleSheet("""
            font-size: 12px;
            font-weight: bold;
            color: #6366f1;
            padding: 2px 8px;
            background-color: #eef2ff;
            border-radius: 4px;
        """)
        header.setFixedWidth(70)
        layout.addWidget(header)
        
        # Explicación
        explanation_label = QLabel(explanation)
        explanation_label.setWordWrap(True)
        explanation_label.setStyleSheet("""
            font-size: 13px;
            color: #334155;
            padding: 4px 0;
        """)
        layout.addWidget(explanation_label)
        
        # Renderizado matemático
        self.math_render = MathRenderWidget()
        self.math_render.render_latex(latex)
        layout.addWidget(self.math_render)


class ChatMessageWidget(QFrame):
    """Widget para mostrar mensajes en el chat."""
    
    def __init__(self, sender: str, message: str, is_user: bool = True, parent=None):
        super().__init__(parent)
        
        if is_user:
            self.setStyleSheet("""
                QFrame {
                    background-color: #e0e7ff;
                    border-radius: 12px;
                    margin: 2px 40px 2px 2px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #ffffff;
                    border: 1px solid #e2e8f0;
                    border-radius: 12px;
                    margin: 2px 2px 2px 40px;
                }
            """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)
        
        # Sender label
        sender_label = QLabel(sender)
        sender_label.setStyleSheet(f"""
            font-size: 11px;
            font-weight: bold;
            color: {'#4f46e5' if is_user else '#059669'};
        """)
        layout.addWidget(sender_label)
        
        # Message
        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("""
            font-size: 13px;
            color: #1e293b;
        """)
        layout.addWidget(msg_label)


class SolverView(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = StepEngine()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6366f1, stop:1 #8b5cf6);
                border-radius: 12px;
                padding: 5px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 12, 15, 12)
        
        header = QLabel("🧮 The Solver - Resolutor de Ecuaciones Diferenciales")
        header.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: white;
        """)
        header_layout.addWidget(header)
        header_layout.addStretch()
        
        # Toggle keyboard button
        self.toggle_keyboard_btn = QPushButton("⌨ Teclado")
        self.toggle_keyboard_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255,255,255,0.2);
                border: 1px solid rgba(255,255,255,0.3);
                border-radius: 6px;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.3);
            }
        """)
        self.toggle_keyboard_btn.clicked.connect(self._toggle_keyboard)
        header_layout.addWidget(self.toggle_keyboard_btn)
        
        layout.addWidget(header_frame)
        
        # Crear splitter para área de chat y teclado
        self.main_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Chat History Area
        chat_container = QWidget()
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area para el historial
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.chat_scroll.setStyleSheet("""
            QScrollArea {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            }
        """)
        
        # Widget contenedor para mensajes
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setContentsMargins(10, 10, 10, 10)
        self.chat_layout.setSpacing(8)
        self.chat_layout.addStretch()
        
        self.chat_scroll.setWidget(self.chat_widget)
        chat_layout.addWidget(self.chat_scroll)
        
        self.main_splitter.addWidget(chat_container)
        
        # Math Keyboard (inicialmente oculto)
        self.keyboard_container = QWidget()
        keyboard_layout = QVBoxLayout(self.keyboard_container)
        keyboard_layout.setContentsMargins(0, 0, 0, 0)
        
        self.math_keyboard = MathKeyboard()
        keyboard_layout.addWidget(self.math_keyboard)
        
        self.main_splitter.addWidget(self.keyboard_container)
        self.keyboard_container.hide()  # Oculto por defecto
        
        layout.addWidget(self.main_splitter, 1)
        
        # Input Area
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(12, 10, 12, 10)
        input_layout.setSpacing(10)
        
        self.input_field = QLineEdit()
        self.input_field.setObjectName("input_field")
        self.input_field.setPlaceholderText("Escribe tu ecuación aquí (ej. y' + 2y = e^x, dy/dx = xy)...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                font-size: 15px;
                padding: 10px 15px;
                border: none;
                background-color: transparent;
            }
        """)
        self.input_field.returnPressed.connect(self._handle_send)
        input_layout.addWidget(self.input_field)
        
        # Conectar el teclado matemático al campo de entrada
        self.math_keyboard.set_target_input(self.input_field)
        
        self.send_btn = QPushButton("Resolver ➤")
        self.send_btn.setObjectName("send_btn")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #6366f1;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 10px 20px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #4f46e5;
            }
            QPushButton:pressed {
                background-color: #4338ca;
            }
        """)
        self.send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_btn.clicked.connect(self._handle_send)
        input_layout.addWidget(self.send_btn)
        
        layout.addWidget(input_frame)
        
        # Mantener compatibilidad con tests existentes (oculto pero parte del árbol de widgets)
        self.chat_history = QListWidget(self)
        self.chat_history.setObjectName("chat_history")
        self.chat_history.setMaximumHeight(0)
        self.chat_history.setVisible(False)
        layout.addWidget(self.chat_history)

    def _toggle_keyboard(self):
        """Muestra u oculta el teclado matemático."""
        if self.keyboard_container.isVisible():
            self.keyboard_container.hide()
            self.toggle_keyboard_btn.setText("⌨ Teclado")
        else:
            self.keyboard_container.show()
            self.toggle_keyboard_btn.setText("✕ Cerrar")
    
    def _add_message(self, sender: str, message: str, is_user: bool = True):
        """Añade un mensaje al historial del chat."""
        msg_widget = ChatMessageWidget(sender, message, is_user)
        
        # Insertar antes del stretch
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, msg_widget)
        
        # Scroll al final
        self.chat_scroll.verticalScrollBar().setValue(
            self.chat_scroll.verticalScrollBar().maximum()
        )
        
        # Mantener compatibilidad con tests
        self.chat_history.addItem(f"{sender}: {message}")
    
    def _add_solution_step(self, step_number: int, explanation: str, latex: str):
        """Añade un paso de solución con renderizado matemático."""
        step_widget = SolutionStepWidget(step_number, explanation, latex)
        
        # Insertar antes del stretch
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, step_widget)
        
        # Scroll al final
        self.chat_scroll.verticalScrollBar().setValue(
            self.chat_scroll.verticalScrollBar().maximum()
        )
        
        # Mantener compatibilidad con tests
        self.chat_history.addItem(f"Solver: {explanation}")
        self.chat_history.addItem(f"        [ {latex} ]")

    def _handle_send(self):
        text = self.input_field.text().strip()
        if text:
            # Add User message
            self._add_message("Tú", text, is_user=True)
            self.input_field.clear()
            
            # Simple heuristic to transform user input to Engine format
            # This is a basic integration for demonstration
            # In a real app, we'd need a robust parser from 'y' + 2y' to SymPy objects
            engine_input = text
            if "y'" in text:
                engine_input = text.replace("y'", "Derivative(y(x), x)").replace("e^x", "exp(x)")
                # Remove spaces and normalize multiplication for basic parsing if needed
            
            self._add_message("Solver", "¡Entendido! Analizando tu ecuación...", is_user=False)
            
            try:
                steps = self.engine.solve_steps(engine_input)
                if steps:
                    for i, step in enumerate(steps, 1):
                        self._add_solution_step(i, step.explanation, step.latex)
                else:
                    self._add_message("Solver", "No pude encontrar pasos para esta ecuación aún. Intenta con otro formato.", is_user=False)
            except Exception as e:
                self._add_message("Solver", f"Ocurrió un error al procesar: {str(e)}", is_user=False)