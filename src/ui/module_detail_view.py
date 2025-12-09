from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget,
                             QHBoxLayout, QFrame, QMessageBox, QDialog, QLineEdit,
                             QDialogButtonBox, QScrollArea, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, QUrl
from PyQt6.QtGui import QDesktopServices
from src.ui.math_keyboard import MathKeyboard, MathRenderWidget


class ExerciseDialog(QDialog):
    """
    Diálogo interactivo para resolver ejercicios con teclado matemático.
    """
    
    def __init__(self, exercise_data: dict, parent=None):
        super().__init__(parent)
        self.exercise_data = exercise_data
        self.setWindowTitle("📝 Ejercicio Interactivo")
        self.setMinimumSize(700, 600)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Encabezado del ejercicio
        header = QLabel(self.exercise_data.get("title", "Ejercicio"))
        header.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #1e293b;
            padding-bottom: 10px;
            border-bottom: 2px solid #e2e8f0;
        """)
        layout.addWidget(header)
        
        # Descripción del problema
        problem_frame = QFrame()
        problem_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f9ff;
                border: 1px solid #bae6fd;
                border-radius: 12px;
            }
        """)
        problem_layout = QVBoxLayout(problem_frame)
        problem_layout.setContentsMargins(15, 15, 15, 15)
        
        problem_label = QLabel("📋 Problema:")
        problem_label.setStyleSheet("font-weight: bold; color: #0369a1; font-size: 14px;")
        problem_layout.addWidget(problem_label)
        
        problem_text = QLabel(self.exercise_data.get("problem", ""))
        problem_text.setWordWrap(True)
        problem_text.setStyleSheet("font-size: 15px; color: #1e293b; line-height: 1.5;")
        problem_layout.addWidget(problem_text)
        
        # Renderizado de la ecuación si existe
        if "equation" in self.exercise_data:
            self.equation_render = MathRenderWidget()
            self.equation_render.render_latex(self.exercise_data["equation"])
            problem_layout.addWidget(self.equation_render)
        
        layout.addWidget(problem_frame)
        
        # Área de respuesta
        answer_frame = QFrame()
        answer_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        answer_layout = QVBoxLayout(answer_frame)
        answer_layout.setContentsMargins(15, 15, 15, 15)
        
        answer_label = QLabel("✍️ Tu Respuesta:")
        answer_label.setStyleSheet("font-weight: bold; color: #059669; font-size: 14px;")
        answer_layout.addWidget(answer_label)
        
        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("Escribe tu respuesta aquí...")
        self.answer_input.setStyleSheet("""
            QLineEdit {
                font-size: 16px;
                padding: 12px 15px;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                background-color: #fafafa;
            }
            QLineEdit:focus {
                border-color: #6366f1;
                background-color: white;
            }
        """)
        answer_layout.addWidget(self.answer_input)
        
        # Teclado matemático
        self.math_keyboard = MathKeyboard(target_input=self.answer_input)
        answer_layout.addWidget(self.math_keyboard)
        
        layout.addWidget(answer_frame)
        
        # Área de hints
        self.hint_label = QLabel("")
        self.hint_label.setWordWrap(True)
        self.hint_label.setStyleSheet("""
            font-size: 13px;
            color: #64748b;
            padding: 10px;
            background-color: #fef3c7;
            border-radius: 8px;
        """)
        self.hint_label.hide()
        layout.addWidget(self.hint_label)
        
        # Área de feedback
        self.feedback_label = QLabel("")
        self.feedback_label.setWordWrap(True)
        self.feedback_label.hide()
        layout.addWidget(self.feedback_label)
        
        # Botones de acción
        button_layout = QHBoxLayout()
        
        hint_btn = QPushButton("💡 Pista")
        hint_btn.setStyleSheet("""
            QPushButton {
                background-color: #fef3c7;
                color: #92400e;
                border: 1px solid #fcd34d;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #fde68a;
            }
        """)
        hint_btn.clicked.connect(self._show_hint)
        button_layout.addWidget(hint_btn)
        
        button_layout.addStretch()
        
        check_btn = QPushButton("✓ Verificar")
        check_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 25px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        check_btn.clicked.connect(self._check_answer)
        button_layout.addWidget(check_btn)
        
        close_btn = QPushButton("Cerrar")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                color: #64748b;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def _show_hint(self):
        """Muestra una pista para el ejercicio."""
        hint = self.exercise_data.get("hint", "Piensa en los conceptos fundamentales.")
        self.hint_label.setText(f"💡 Pista: {hint}")
        self.hint_label.show()
    
    def _check_answer(self):
        """Verifica la respuesta del usuario."""
        user_answer = self.answer_input.text().strip().lower()
        correct_answers = self.exercise_data.get("answers", [])
        
        # Normalizar respuestas para comparación
        user_answer_normalized = user_answer.replace(" ", "").replace("(", "").replace(")", "")
        
        is_correct = False
        for answer in correct_answers:
            answer_normalized = answer.lower().replace(" ", "").replace("(", "").replace(")", "")
            if user_answer_normalized == answer_normalized:
                is_correct = True
                break
        
        if is_correct:
            self.feedback_label.setText("🎉 ¡Correcto! Excelente trabajo.")
            self.feedback_label.setStyleSheet("""
                font-size: 14px;
                padding: 15px;
                background-color: #dcfce7;
                color: #166534;
                border-radius: 8px;
                border: 1px solid #86efac;
            """)
        else:
            explanation = self.exercise_data.get("explanation", "Revisa los conceptos y vuelve a intentarlo.")
            self.feedback_label.setText(f"❌ Respuesta incorrecta.\n\n{explanation}")
            self.feedback_label.setStyleSheet("""
                font-size: 14px;
                padding: 15px;
                background-color: #fee2e2;
                color: #991b1b;
                border-radius: 8px;
                border: 1px solid #fca5a5;
            """)
        
        self.feedback_label.show()


class ModuleDetailView(QWidget):
    back_requested = pyqtSignal()

    # Ejercicios predefinidos para cada módulo
    EXERCISES_DATA = {
        "📝 Ejercicio 1: Identificar Variable Dependiente e Independiente": {
            "title": "Variables en una EDO",
            "problem": "En la ecuación dy/dx + 2y = e^x, identifica:\n\n"
                      "a) La variable dependiente\n"
                      "b) La variable independiente",
            "equation": r"\frac{dy}{dx} + 2y = e^x",
            "hint": "La variable dependiente es la que buscamos resolver (la función). "
                   "La variable independiente es respecto a la cual se deriva.",
            "answers": ["y, x", "y,x", "y x", "dependiente: y, independiente: x"],
            "explanation": "En esta EDO:\n"
                          "• Variable dependiente: y (es la función que queremos encontrar)\n"
                          "• Variable independiente: x (es respecto a la cual derivamos)"
        },
        "📝 Ejercicio 2: Determinar el Orden de la Ecuación": {
            "title": "Orden de una EDO",
            "problem": "¿Cuál es el orden de la siguiente ecuación diferencial?\n\n"
                      "d²y/dx² + 3(dy/dx) - 2y = sin(x)",
            "equation": r"\frac{d^2y}{dx^2} + 3\frac{dy}{dx} - 2y = \sin(x)",
            "hint": "El orden de una EDO es el de la derivada de mayor orden que aparece.",
            "answers": ["2", "segundo", "segundo orden", "orden 2", "dos"],
            "explanation": "El orden es 2, porque la derivada de mayor orden presente es d²y/dx² (segunda derivada)."
        },
        "📝 Ejercicio 3: Verificar si es Lineal o No Lineal": {
            "title": "Linealidad de una EDO",
            "problem": "Determina si la siguiente ecuación es lineal o no lineal:\n\n"
                      "y' + y² = x",
            "equation": r"y' + y^2 = x",
            "hint": "Una EDO es lineal si la variable dependiente y sus derivadas aparecen "
                   "con exponente 1 y no se multiplican entre sí.",
            "answers": ["no lineal", "nolineal", "no-lineal", "no es lineal"],
            "explanation": "La ecuación NO es lineal porque y aparece elevada al cuadrado (y²). "
                          "En una EDO lineal, y y sus derivadas solo pueden aparecer con exponente 1."
        }
    }

    def __init__(self, module_data: dict):
        super().__init__()
        self.module_data = module_data
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header with Back Button
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6366f1, stop:1 #8b5cf6);
                border-radius: 16px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(25, 20, 25, 20)
        
        # Back button row
        back_row = QHBoxLayout()
        self.back_btn = QPushButton("← Volver al Dashboard")
        self.back_btn.setObjectName("back_btn")
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255,255,255,0.2);
                color: white;
                border: 1px solid rgba(255,255,255,0.3);
                border-radius: 8px;
                font-weight: bold;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.3);
            }
        """)
        self.back_btn.clicked.connect(self.back_requested.emit)
        back_row.addWidget(self.back_btn)
        back_row.addStretch()
        header_layout.addLayout(back_row)
        
        # Module Title
        self.title_label = QLabel(self.module_data.get("title", "Módulo"))
        self.title_label.setObjectName("module_title")
        self.title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: 800;
            color: white;
            margin-top: 10px;
        """)
        header_layout.addWidget(self.title_label)
        
        # Description
        desc_label = QLabel(self.module_data.get("description", ""))
        desc_label.setStyleSheet("font-size: 14px; color: rgba(255,255,255,0.9);")
        desc_label.setWordWrap(True)
        header_layout.addWidget(desc_label)
        
        layout.addWidget(header_frame)
        
        # Content Layout
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # Left: Resources (Tutorials, Readings)
        resources_frame = QFrame()
        resources_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }
        """)
        res_layout = QVBoxLayout(resources_frame)
        res_layout.setContentsMargins(20, 20, 20, 20)
        
        res_header = QLabel("📚 Recursos de Aprendizaje")
        res_header.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #1e293b;
            padding-bottom: 10px;
            border-bottom: 2px solid #e2e8f0;
        """)
        res_layout.addWidget(res_header)
        
        self.resources_list = QListWidget()
        self.resources_list.setObjectName("resources_list")
        self.resources_list.addItems(self.module_data.get("resources", []))
        self.resources_list.itemClicked.connect(self._handle_resource_click)
        self.resources_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: transparent;
            }
            QListWidget::item {
                padding: 12px;
                border-radius: 8px;
                margin: 4px 0;
                background-color: #f8fafc;
            }
            QListWidget::item:hover {
                background-color: #e0e7ff;
            }
            QListWidget::item:selected {
                background-color: #c7d2fe;
                color: #1e293b;
            }
        """)
        res_layout.addWidget(self.resources_list)
        
        content_layout.addWidget(resources_frame)
        
        # Right: Exercises
        exercises_frame = QFrame()
        exercises_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }
        """)
        ex_layout = QVBoxLayout(exercises_frame)
        ex_layout.setContentsMargins(20, 20, 20, 20)
        
        ex_header = QLabel("✏️ Ejercicios Interactivos")
        ex_header.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #1e293b;
            padding-bottom: 10px;
            border-bottom: 2px solid #e2e8f0;
        """)
        ex_layout.addWidget(ex_header)
        
        ex_hint = QLabel("💡 Haz clic en un ejercicio para resolverlo con el teclado matemático")
        ex_hint.setStyleSheet("font-size: 12px; color: #64748b; padding: 5px 0;")
        ex_layout.addWidget(ex_hint)
        
        self.exercises_list = QListWidget()
        self.exercises_list.setObjectName("exercises_list")
        self.exercises_list.addItems(self.module_data.get("exercises", []))
        self.exercises_list.itemClicked.connect(self._handle_exercise_click)
        self.exercises_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: transparent;
            }
            QListWidget::item {
                padding: 12px;
                border-radius: 8px;
                margin: 4px 0;
                background-color: #fef3c7;
            }
            QListWidget::item:hover {
                background-color: #fde68a;
            }
            QListWidget::item:selected {
                background-color: #fcd34d;
                color: #1e293b;
            }
        """)
        ex_layout.addWidget(self.exercises_list)
        
        content_layout.addWidget(exercises_frame)
        
        layout.addLayout(content_layout, stretch=1)

    def _handle_resource_click(self, item):
        text = item.text()
        if "Video" in text:
            # Video Link Logic
            url = QUrl("https://www.youtube.com/watch?v=U7L2XmS7dl0&t=462s")
            QDesktopServices.openUrl(url)
        elif "Lectura" in text:
            # Reading Logic (Dialog for now)
            QMessageBox.information(self, "📖 Recurso de Lectura",
                "<h3>Conceptos Fundamentales de EDOs</h3>"
                "<p>Una <b>Ecuación Diferencial Ordinaria (EDO)</b> relaciona una función "
                "desconocida de una variable independiente con sus derivadas.</p>"
                "<h4>Orden:</h4>"
                "<p>La derivada más alta presente en la ecuación.</p>"
                "<h4>Linealidad:</h4>"
                "<p>La variable dependiente y sus derivadas aparecen con potencia 1 "
                "y no multiplicadas entre sí.</p>"
                "<h4>Ejemplos:</h4>"
                "<ul>"
                "<li>y' + 2y = 0 → Lineal de primer orden</li>"
                "<li>y'' + y = sin(x) → Lineal de segundo orden</li>"
                "<li>y' = y² → No lineal de primer orden</li>"
                "</ul>")

    def _handle_exercise_click(self, item):
        """Abre el diálogo interactivo para resolver el ejercicio."""
        exercise_name = item.text()
        
        # Buscar datos del ejercicio
        if exercise_name in self.EXERCISES_DATA:
            exercise_data = self.EXERCISES_DATA[exercise_name]
        else:
            # Ejercicio genérico
            exercise_data = {
                "title": exercise_name,
                "problem": f"Resuelve el siguiente problema:\n\n{exercise_name}",
                "hint": "Piensa en los conceptos fundamentales que has aprendido.",
                "answers": [],
                "explanation": "Consulta los recursos de aprendizaje para más información."
            }
        
        # Abrir diálogo
        dialog = ExerciseDialog(exercise_data, self)
        dialog.exec()