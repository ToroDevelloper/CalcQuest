"""
Vista de ejercicios interactivos con sistema de niveles.
Diseño moderno con categorías, dificultad y progreso.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QScrollArea, QGridLayout, QDialog, QLineEdit, QProgressBar,
    QStackedWidget, QButtonGroup, QRadioButton, QSizePolicy,
    QGraphicsDropShadowEffect, QMessageBox, QTabWidget, QSpacerItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QFont
import json
import time
import re

from src.ui.math_keyboard import MathKeyboard, MathRenderWidget


class LevelBadge(QLabel):
    """Badge que muestra el nivel de dificultad."""
    
    def __init__(self, nivel_nombre: str, color: str, icono: str, parent=None):
        super().__init__(parent)
        self.setText(f"{icono} {nivel_nombre}")
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                font-size: 11px;
                font-weight: bold;
                padding: 4px 10px;
                border-radius: 12px;
            }}
        """)
        self.setFixedHeight(24)


class ExerciseCard(QFrame):
    """Tarjeta de ejercicio en la lista."""
    
    clicked = pyqtSignal(dict)
    
    def __init__(self, exercise_data: dict, parent=None):
        super().__init__(parent)
        self.exercise_data = exercise_data
        self._setup_ui()
    
    def _setup_ui(self):
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        is_completed = self.exercise_data.get('completado', False)
        nivel_color = self.exercise_data.get('nivel_color', '#6366f1')
        
        # Estilo según estado
        if is_completed:
            bg_color = "#ecfdf5"
            border_color = "#10b981"
            status_icon = "✅"
        else:
            bg_color = "white"
            border_color = "#e2e8f0"
            status_icon = "📝"
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 2px solid {border_color};
                border-radius: 12px;
            }}
            QFrame:hover {{
                border-color: {nivel_color};
                background-color: #f8fafc;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(12)
        
        # Icono de estado
        status_label = QLabel(status_icon)
        status_label.setStyleSheet("font-size: 20px;")
        status_label.setFixedWidth(30)
        layout.addWidget(status_label)
        
        # Info del ejercicio
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        # Título
        title = QLabel(self.exercise_data.get('titulo', 'Ejercicio'))
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #1e293b;")
        info_layout.addWidget(title)
        
        # Subtítulo con XP y tiempo
        xp = self.exercise_data.get('xp_base', 25)
        tiempo = self.exercise_data.get('tiempo_limite_segundos', 180) // 60
        
        meta_layout = QHBoxLayout()
        meta_layout.setSpacing(15)
        
        xp_label = QLabel(f"⭐ {xp} XP")
        xp_label.setStyleSheet("font-size: 12px; color: #f59e0b;")
        meta_layout.addWidget(xp_label)
        
        time_label = QLabel(f"⏱️ {tiempo} min")
        time_label.setStyleSheet("font-size: 12px; color: #64748b;")
        meta_layout.addWidget(time_label)
        
        if self.exercise_data.get('intentos', 0) > 0:
            attempts = QLabel(f"🔄 {self.exercise_data['intentos']} intentos")
            attempts.setStyleSheet("font-size: 12px; color: #94a3b8;")
            meta_layout.addWidget(attempts)
        
        meta_layout.addStretch()
        info_layout.addLayout(meta_layout)
        
        layout.addLayout(info_layout, stretch=1)
        
        # Badge de nivel
        nivel_badge = LevelBadge(
            self.exercise_data.get('nivel_nombre', 'Básico'),
            nivel_color,
            self.exercise_data.get('nivel_icono', '⭐')
        )
        layout.addWidget(nivel_badge)
        
        # Flecha
        arrow = QLabel("→")
        arrow.setStyleSheet("font-size: 18px; color: #94a3b8;")
        layout.addWidget(arrow)
    
    def mousePressEvent(self, event):
        # Emitimos la señal sin llamar a super para evitar que Qt procese clicks
        # sobre un widget que podría ser destruido al recargar la lista.
        self.clicked.emit(self.exercise_data)


class CategoryCard(QFrame):
    """Tarjeta de categoría/tema."""
    
    clicked = pyqtSignal(dict)
    
    def __init__(self, category_data: dict, parent=None):
        super().__init__(parent)
        self.category_data = category_data
        self._setup_ui()
    
    def _setup_ui(self):
        is_unlocked = self.category_data.get('desbloqueado', True)
        
        if is_unlocked:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            bg_color = "white"
            opacity = "1"
        else:
            bg_color = "#f8fafc"
            opacity = "0.6"
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }}
            QFrame:hover {{
                border-color: #6366f1;
            }}
        """)
        
        # Sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # Header con icono y lock
        header = QHBoxLayout()
        
        icon = QLabel(self.category_data.get('icono', '📚'))
        icon.setStyleSheet("""
            font-size: 32px;
            background-color: #eef2ff;
            padding: 10px;
            border-radius: 12px;
        """)
        icon.setFixedSize(55, 55)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.addWidget(icon)
        
        header.addStretch()
        
        if not is_unlocked:
            lock = QLabel("🔒")
            lock.setStyleSheet("font-size: 24px;")
            header.addWidget(lock)
        else:
            nivel_req = self.category_data.get('nivel_requerido', 1)
            nivel_label = QLabel(f"Nv.{nivel_req}")
            nivel_label.setStyleSheet("""
                background-color: #ddd6fe;
                color: #7c3aed;
                font-size: 11px;
                font-weight: bold;
                padding: 4px 8px;
                border-radius: 10px;
            """)
            header.addWidget(nivel_label)
        
        layout.addLayout(header)
        
        # Título
        title = QLabel(self.category_data.get('nombre', 'Categoría'))
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1e293b;")
        title.setWordWrap(True)
        layout.addWidget(title)
        
        # Descripción
        desc = QLabel(self.category_data.get('descripcion', ''))
        desc.setStyleSheet("font-size: 12px; color: #64748b;")
        desc.setWordWrap(True)
        desc.setMaximumHeight(40)
        layout.addWidget(desc)
        
        # Progreso
        total = self.category_data.get('total_ejercicios', 0)
        completed = self.category_data.get('ejercicios_completados', 0)
        
        if total > 0 and is_unlocked:
            progress_layout = QHBoxLayout()
            
            progress_bar = QProgressBar()
            progress_bar.setRange(0, total)
            progress_bar.setValue(completed)
            progress_bar.setTextVisible(False)
            progress_bar.setFixedHeight(6)
            progress_bar.setStyleSheet("""
                QProgressBar {
                    background-color: #e2e8f0;
                    border-radius: 3px;
                }
                QProgressBar::chunk {
                    background-color: #10b981;
                    border-radius: 3px;
                }
            """)
            progress_layout.addWidget(progress_bar)
            
            progress_text = QLabel(f"{completed}/{total}")
            progress_text.setStyleSheet("font-size: 11px; color: #64748b; font-weight: bold;")
            progress_layout.addWidget(progress_text)
            
            layout.addLayout(progress_layout)
        
        self.setMinimumHeight(220)
        # Expand to available width so cards no longer look tiny
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    
    def mousePressEvent(self, event):
        if self.category_data.get('desbloqueado', True):
            self.clicked.emit(self.category_data)
        super().mousePressEvent(event)


class ExerciseDialog(QDialog):
    """
    Diálogo mejorado para resolver ejercicios.
    Incluye temporizador, múltiples tipos de respuesta, y feedback visual.
    """
    
    exercise_completed = pyqtSignal(dict)  # Emite resultado del ejercicio
    
    def __init__(self, exercise_data: dict, parent=None):
        super().__init__(parent)
        self.exercise_data = exercise_data
        self.start_time = time.time()
        self.attempts = 0
        self.hint_shown = False
        
        self.setWindowTitle(f"📝 {exercise_data.get('titulo', 'Ejercicio')}")
        # Larger default dialog for better readability
        self.setMinimumSize(1000, 800)
        self._setup_ui()
        self._start_timer()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header con info del ejercicio
        header = self._create_header()
        layout.addWidget(header)
        
        # Contenido principal con scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: #f8fafc; }")
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(30, 25, 30, 25)
        content_layout.setSpacing(20)
        
        # Problema
        problem_frame = self._create_problem_section()
        content_layout.addWidget(problem_frame)
        
        # Área de respuesta
        answer_frame = self._create_answer_section()
        content_layout.addWidget(answer_frame)
        
        # Hint y feedback (inicialmente ocultos)
        self.hint_frame = self._create_hint_section()
        self.hint_frame.hide()
        content_layout.addWidget(self.hint_frame)
        
        self.feedback_frame = self._create_feedback_section()
        self.feedback_frame.hide()
        content_layout.addWidget(self.feedback_frame)
        
        content_layout.addStretch()
        
        scroll.setWidget(content)
        layout.addWidget(scroll, stretch=1)
        
        # Footer con botones
        footer = self._create_footer()
        layout.addWidget(footer)
    
    def _create_header(self) -> QFrame:
        """Crea el header con información del ejercicio."""
        header = QFrame()
        nivel_color = self.exercise_data.get('nivel_color', '#6366f1')
        
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {nivel_color}, stop:1 #8b5cf6);
                border-bottom: 1px solid #e2e8f0;
            }}
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(25, 15, 25, 15)
        
        # Info izquierda
        left_layout = QVBoxLayout()
        
        # Categoría y nivel
        cat_label = QLabel(f"{self.exercise_data.get('categoria_nombre', 'Categoría')} • {self.exercise_data.get('nivel_nombre', 'Nivel')}")
        cat_label.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.8);")
        left_layout.addWidget(cat_label)
        
        # Título
        title = QLabel(self.exercise_data.get('titulo', 'Ejercicio'))
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        left_layout.addWidget(title)
        
        layout.addLayout(left_layout)
        layout.addStretch()
        
        # Info derecha
        right_layout = QHBoxLayout()
        right_layout.setSpacing(20)
        
        # XP
        xp = self.exercise_data.get('xp_base', 25)
        xp_label = QLabel(f"⭐ {xp} XP")
        xp_label.setStyleSheet("font-size: 14px; color: white; font-weight: bold;")
        right_layout.addWidget(xp_label)
        
        # Temporizador
        self.timer_label = QLabel("⏱️ 00:00")
        self.timer_label.setStyleSheet("""
            font-size: 14px;
            color: white;
            font-weight: bold;
            background-color: rgba(0,0,0,0.2);
            padding: 5px 12px;
            border-radius: 15px;
        """)
        right_layout.addWidget(self.timer_label)
        
        layout.addLayout(right_layout)
        
        return header
    
    def _create_problem_section(self) -> QFrame:
        """Crea la sección del problema."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)
        
        # Etiqueta
        label = QLabel("📋 Problema")
        label.setStyleSheet("font-size: 14px; font-weight: bold; color: #0369a1;")
        layout.addWidget(label)
        
        # Texto del problema
        problem_text = QLabel(self.exercise_data.get('problema', ''))
        problem_text.setWordWrap(True)
        problem_text.setStyleSheet("font-size: 15px; color: #1e293b; line-height: 1.6;")
        layout.addWidget(problem_text)
        
        # Ecuación renderizada
        if self.exercise_data.get('ecuacion_latex'):
            equation_widget = MathRenderWidget()
            equation_widget.setMinimumHeight(80)
            equation_widget.render_latex(self.exercise_data['ecuacion_latex'])
            layout.addWidget(equation_widget)
        
        return frame
    
    def _create_answer_section(self) -> QFrame:
        """Crea la sección de respuesta según el tipo."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)
        
        # Etiqueta
        label = QLabel("✍️ Tu Respuesta")
        label.setStyleSheet("font-size: 14px; font-weight: bold; color: #059669;")
        layout.addWidget(label)
        
        tipo_respuesta = self.exercise_data.get('tipo_respuesta', 'texto')
        
        if tipo_respuesta == 'opcion_multiple':
            # Opciones múltiples
            self.option_group = QButtonGroup(self)
            options = self.exercise_data.get('opciones', [])
            
            for i, option in enumerate(options):
                radio = QRadioButton(option)
                radio.setStyleSheet("""
                    QRadioButton {
                        font-size: 14px;
                        padding: 12px;
                        background-color: #f8fafc;
                        border-radius: 8px;
                        margin: 4px 0;
                    }
                    QRadioButton:hover {
                        background-color: #e0e7ff;
                    }
                    QRadioButton:checked {
                        background-color: #c7d2fe;
                    }
                """)
                self.option_group.addButton(radio, i)
                layout.addWidget(radio)
            
            self.answer_input = None
        else:
            # Campo de texto con teclado matemático
            self.answer_input = QLineEdit()
            self.answer_input.setPlaceholderText("Escribe tu respuesta aquí...")
            self.answer_input.setStyleSheet("""
                QLineEdit {
                    font-size: 16px;
                    padding: 15px;
                    border: 2px solid #e2e8f0;
                    border-radius: 12px;
                    background-color: #fafafa;
                }
                QLineEdit:focus {
                    border-color: #6366f1;
                    background-color: white;
                }
            """)
            layout.addWidget(self.answer_input)
            
            # Teclado matemático compacto
            self.math_keyboard = MathKeyboard(target_input=self.answer_input)
            self.math_keyboard.setMaximumHeight(260)
            layout.addWidget(self.math_keyboard)
            
            self.option_group = None
        
        return frame
    
    def _create_hint_section(self) -> QFrame:
        """Crea la sección de pista."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #fef3c7;
                border: 1px solid #fcd34d;
                border-radius: 12px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 15, 20, 15)
        
        hint_text = self.exercise_data.get('pista', 'Piensa en los conceptos fundamentales.')
        self.hint_label = QLabel(f"💡 Pista: {hint_text}")
        self.hint_label.setWordWrap(True)
        self.hint_label.setStyleSheet("font-size: 13px; color: #92400e;")
        layout.addWidget(self.hint_label)
        
        return frame
    
    def _create_feedback_section(self) -> QFrame:
        """Crea la sección de feedback."""
        frame = QFrame()
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 15, 20, 15)
        
        self.feedback_icon = QLabel("")
        self.feedback_icon.setStyleSheet("font-size: 32px;")
        self.feedback_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.feedback_icon)
        
        self.feedback_title = QLabel("")
        self.feedback_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.feedback_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.feedback_title)
        
        self.feedback_text = QLabel("")
        self.feedback_text.setWordWrap(True)
        self.feedback_text.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.feedback_text)
        
        self.xp_earned_label = QLabel("")
        self.xp_earned_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.xp_earned_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.xp_earned_label.hide()
        layout.addWidget(self.xp_earned_label)
        
        return frame
    
    def _create_footer(self) -> QFrame:
        """Crea el footer con botones."""
        footer = QFrame()
        footer.setStyleSheet("""
            QFrame {
                background-color: white;
                border-top: 1px solid #e2e8f0;
            }
        """)
        
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(25, 15, 25, 15)
        
        # Botón de pista
        self.hint_btn = QPushButton("💡 Pista")
        self.hint_btn.setStyleSheet("""
            QPushButton {
                background-color: #fef3c7;
                color: #92400e;
                border: 1px solid #fcd34d;
                border-radius: 10px;
                padding: 12px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #fde68a;
            }
        """)
        self.hint_btn.clicked.connect(self._show_hint)
        layout.addWidget(self.hint_btn)
        
        layout.addStretch()
        
        # Botón verificar
        self.check_btn = QPushButton("✓ Verificar Respuesta")
        self.check_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 30px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.check_btn.clicked.connect(self._check_answer)
        layout.addWidget(self.check_btn)
        
        # Botón continuar (oculto inicialmente)
        self.continue_btn = QPushButton("Continuar →")
        self.continue_btn.setStyleSheet("""
            QPushButton {
                background-color: #6366f1;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 30px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4f46e5;
            }
        """)
        self.continue_btn.clicked.connect(self.accept)
        self.continue_btn.hide()
        layout.addWidget(self.continue_btn)
        
        # Botón cerrar
        close_btn = QPushButton("Cerrar")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                color: #64748b;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 12px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        close_btn.clicked.connect(self.reject)
        layout.addWidget(close_btn)
        
        return footer
    
    def _start_timer(self):
        """Inicia el temporizador."""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_timer)
        self.timer.start(1000)
    
    def _update_timer(self):
        """Actualiza el display del temporizador."""
        elapsed = int(time.time() - self.start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        self.timer_label.setText(f"⏱️ {minutes:02d}:{seconds:02d}")
        
        # Advertencia si se acerca al límite
        tiempo_limite = self.exercise_data.get('tiempo_limite_segundos', 300)
        if elapsed > tiempo_limite * 0.8:
            self.timer_label.setStyleSheet("""
                font-size: 14px;
                color: #fef3c7;
                font-weight: bold;
                background-color: #ef4444;
                padding: 5px 12px;
                border-radius: 15px;
            """)
    
    def _show_hint(self):
        """Muestra la pista."""
        self.hint_frame.show()
        self.hint_shown = True
        self.hint_btn.setEnabled(False)
        self.hint_btn.setText("💡 Pista mostrada")
    
    def _check_answer(self):
        """Verifica la respuesta del usuario."""
        self.attempts += 1

        def _normalize(text: str) -> str:
            # Permite tildes o signos; elimina espacios, paréntesis y signos comunes para ser flexible
            return re.sub(r"[\s\(\),;:.]", "", text.lower())
        
        # Obtener respuesta según tipo
        if self.option_group:
            selected = self.option_group.checkedButton()
            if not selected:
                QMessageBox.warning(self, "Aviso", "Por favor selecciona una opción.")
                return
            user_answer = selected.text().split(" - ")[-1] if " - " in selected.text() else selected.text()
        else:
            user_answer = self.answer_input.text().strip()
            if not user_answer:
                QMessageBox.warning(self, "Aviso", "Por favor escribe tu respuesta.")
                return
        
        # Verificar respuesta
        correct_answers = self.exercise_data.get('respuestas_correctas', [])
        user_normalized = _normalize(user_answer)
        
        is_correct = any(user_normalized == _normalize(ans) for ans in correct_answers)
        
        # Calcular XP
        elapsed_time = int(time.time() - self.start_time)
        xp_base = self.exercise_data.get('xp_base', 25)
        multiplicador = float(self.exercise_data.get('multiplicador_xp', 1.0))
        
        if is_correct:
            if self.attempts == 1 and not self.hint_shown:
                xp_earned = int(xp_base * multiplicador)
            elif self.attempts <= 2:
                xp_earned = int(xp_base * multiplicador * 0.75)
            else:
                xp_earned = int(xp_base * multiplicador * 0.5)
            
            self._show_correct_feedback(xp_earned)
        else:
            self._show_incorrect_feedback()
    
    def _show_correct_feedback(self, xp_earned: int):
        """Muestra feedback de respuesta correcta."""
        self.timer.stop()
        
        self.feedback_frame.setStyleSheet("""
            QFrame {
                background-color: #dcfce7;
                border: 2px solid #86efac;
                border-radius: 16px;
            }
        """)
        
        self.feedback_icon.setText("🎉")
        self.feedback_title.setText("¡Correcto!")
        self.feedback_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #166534;")
        
        explanation = self.exercise_data.get('explicacion', '')
        self.feedback_text.setText(explanation)
        self.feedback_text.setStyleSheet("font-size: 14px; color: #166534;")
        
        self.xp_earned_label.setText(f"⭐ +{xp_earned} XP")
        self.xp_earned_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #f59e0b;")
        self.xp_earned_label.show()
        
        self.feedback_frame.show()
        
        # Cambiar botones
        self.check_btn.hide()
        self.hint_btn.hide()
        self.continue_btn.show()
        
        # Emitir resultado
        elapsed_time = int(time.time() - self.start_time)
        self.exercise_completed.emit({
            'exercise_id': self.exercise_data.get('id'),
            'is_correct': True,
            'xp_earned': xp_earned,
            'time_seconds': elapsed_time,
            'attempts': self.attempts
        })
    
    def _show_incorrect_feedback(self):
        """Muestra feedback de respuesta incorrecta."""
        self.feedback_frame.setStyleSheet("""
            QFrame {
                background-color: #fee2e2;
                border: 2px solid #fca5a5;
                border-radius: 16px;
            }
        """)
        
        self.feedback_icon.setText("❌")
        self.feedback_title.setText("Respuesta incorrecta")
        self.feedback_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #991b1b;")
        
        if self.attempts >= 3:
            explanation = self.exercise_data.get('explicacion', '')
            self.feedback_text.setText(f"Solución:\n{explanation}")
        else:
            self.feedback_text.setText(f"Intento {self.attempts}. ¡Vuelve a intentarlo!")
        
        self.feedback_text.setStyleSheet("font-size: 14px; color: #991b1b;")
        
        self.feedback_frame.show()
        
        # Mostrar pista automáticamente después de 2 intentos
        if self.attempts >= 2 and not self.hint_shown:
            self._show_hint()


class ExercisesView(QWidget):
    """
    Vista principal de ejercicios con categorías y niveles.
    """
    
    back_requested = pyqtSignal()
    exercise_completed = pyqtSignal(dict)
    
    def __init__(self, db=None, user_id: int = None):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.current_category = None
        self._setup_ui()
        self._load_data()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Stack para categorías y ejercicios
        self.stack = QStackedWidget()
        
        # Vista de categorías
        self.categories_view = self._create_categories_view()
        self.stack.addWidget(self.categories_view)
        
        # Vista de ejercicios (se llena dinámicamente)
        self.exercises_view = self._create_exercises_view()
        self.stack.addWidget(self.exercises_view)
        
        layout.addWidget(self.stack)
    
    def _create_categories_view(self) -> QWidget:
        """Crea la vista de categorías."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Header
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6366f1, stop:1 #8b5cf6);
                border-radius: 20px;
            }
        """)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(30, 25, 30, 25)
        
        title = QLabel("📚 Ejercicios por Tema")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        header_layout.addWidget(title)
        
        subtitle = QLabel("Selecciona una categoría para practicar. Los temas se desbloquean según tu nivel.")
        subtitle.setStyleSheet("font-size: 14px; color: rgba(255,255,255,0.9);")
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header)
        
        # Scroll area para categorías
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: transparent; }")
        
        self.categories_container = QWidget()
        self.categories_layout = QGridLayout(self.categories_container)
        self.categories_layout.setSpacing(20)
        self.categories_layout.setContentsMargins(5, 10, 5, 10)
        
        scroll.setWidget(self.categories_container)
        layout.addWidget(scroll, stretch=1)
        
        return widget
    
    def _create_exercises_view(self) -> QWidget:
        """Crea la vista de ejercicios de una categoría."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        # Header con botón volver
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        back_btn = QPushButton("← Volver")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                color: #64748b;
                border: none;
                border-radius: 8px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        back_btn.clicked.connect(self._back_to_categories)
        header_layout.addWidget(back_btn)
        
        self.category_title_label = QLabel("Categoría")
        self.category_title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1e293b;")
        header_layout.addWidget(self.category_title_label)
        
        header_layout.addStretch()
        
        self.category_progress_label = QLabel("0/0 completados")
        self.category_progress_label.setStyleSheet("font-size: 14px; color: #64748b;")
        header_layout.addWidget(self.category_progress_label)
        
        layout.addWidget(header)
        
        # Filtros por nivel
        filters = QFrame()
        filters.setStyleSheet("background-color: transparent;")
        filters_layout = QHBoxLayout(filters)
        filters_layout.setContentsMargins(0, 0, 0, 0)
        
        self.filter_buttons = []
        filter_labels = [("Todos", None), ("🌱 Principiante", 1), ("⭐ Básico", 2), 
                        ("🔥 Intermedio", 3), ("💎 Avanzado", 4)]
        
        for label, nivel_id in filter_labels:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setProperty("nivel_id", nivel_id)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    color: #64748b;
                    border: 1px solid #e2e8f0;
                    border-radius: 20px;
                    padding: 8px 16px;
                    font-size: 13px;
                }
                QPushButton:checked {
                    background-color: #6366f1;
                    color: white;
                    border-color: #6366f1;
                }
                QPushButton:hover:!checked {
                    background-color: #f1f5f9;
                }
            """)
            btn.clicked.connect(lambda checked, n=nivel_id: self._filter_exercises(n))
            filters_layout.addWidget(btn)
            self.filter_buttons.append(btn)
        
        self.filter_buttons[0].setChecked(True)
        filters_layout.addStretch()
        
        layout.addWidget(filters)
        
        # Lista de ejercicios
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        self.exercises_container = QWidget()
        self.exercises_list_layout = QVBoxLayout(self.exercises_container)
        self.exercises_list_layout.setSpacing(10)
        self.exercises_list_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll.setWidget(self.exercises_container)
        layout.addWidget(scroll, stretch=1)
        
        return widget
    
    def _load_data(self):
        """Carga las categorías desde la base de datos."""
        if not self.db:
            self._load_mock_categories()
            return
        
        try:
            categories = self.db.get_categories(self.user_id)
            self._display_categories(categories)
        except Exception as e:
            print(f"Error cargando categorías: {e}")
            self._load_mock_categories()
    
    def _load_mock_categories(self):
        """Carga categorías de ejemplo si no hay base de datos."""
        mock_categories = [
            {"id": 1, "nombre": "Introducción a EDOs", "descripcion": "Conceptos básicos", 
             "icono": "📚", "nivel_requerido": 1, "desbloqueado": True, 
             "total_ejercicios": 4, "ejercicios_completados": 2},
            {"id": 2, "nombre": "Derivadas Básicas", "descripcion": "Reglas de derivación", 
             "icono": "📐", "nivel_requerido": 1, "desbloqueado": True,
             "total_ejercicios": 5, "ejercicios_completados": 0},
            {"id": 3, "nombre": "Integrales Básicas", "descripcion": "Técnicas de integración", 
             "icono": "∫", "nivel_requerido": 1, "desbloqueado": True,
             "total_ejercicios": 4, "ejercicios_completados": 0},
            {"id": 4, "nombre": "Variables Separables", "descripcion": "dy/dx = f(x)g(y)", 
             "icono": "🔀", "nivel_requerido": 2, "desbloqueado": False,
             "total_ejercicios": 4, "ejercicios_completados": 0},
            {"id": 5, "nombre": "EDOs Lineales 1er Orden", "descripcion": "Factor integrante", 
             "icono": "📈", "nivel_requerido": 2, "desbloqueado": False,
             "total_ejercicios": 3, "ejercicios_completados": 0},
            {"id": 6, "nombre": "Ecuaciones Exactas", "descripcion": "M dx + N dy = 0", 
             "icono": "⚖️", "nivel_requerido": 3, "desbloqueado": False,
             "total_ejercicios": 2, "ejercicios_completados": 0},
        ]
        self._display_categories(mock_categories)
    
    def _display_categories(self, categories: list):
        """Muestra las categorías en el grid."""
        # Limpiar layout existente
        while self.categories_layout.count():
            item = self.categories_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        row, col = 0, 0
        max_cols = 3
        
        for cat in categories:
            card = CategoryCard(cat)
            card.clicked.connect(self._on_category_clicked)
            self.categories_layout.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Añadir espaciador
        self.categories_layout.setRowStretch(row + 1, 1)
    
    def _on_category_clicked(self, category_data: dict):
        """Maneja el clic en una categoría."""
        self.current_category = category_data
        self._load_exercises(category_data['id'])
        
        # Actualizar header
        self.category_title_label.setText(
            f"{category_data.get('icono', '📚')} {category_data.get('nombre', 'Categoría')}"
        )
        
        self.stack.setCurrentIndex(1)
    
    def _load_exercises(self, categoria_id: int):
        """Carga los ejercicios de una categoría."""
        # Limpiar lista existente
        while self.exercises_list_layout.count():
            item = self.exercises_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if self.db:
            try:
                exercises = self.db.get_exercises_by_category(categoria_id, self.user_id)
                self._display_exercises(exercises)
                return
            except Exception as e:
                print(f"Error cargando ejercicios: {e}")
        
        # Mock exercises con respuestas para que la validación funcione sin BD
        mock_exercises = [
            {
                "id": 1,
                "titulo": "Identificar Variables",
                "xp_base": 20,
                "tiempo_limite_segundos": 180,
                "nivel_nombre": "Principiante",
                "nivel_color": "#22c55e",
                "nivel_icono": "🌱",
                "completado": False,
                "intentos": 0,
                "tipo_respuesta": "texto",
                "problema": "En la ecuación dy/dx + 2y = e^x, identifica la variable dependiente e independiente.",
                "ecuacion_latex": r"\\frac{dy}{dx} + 2y = e^x",
                "pista": "La variable dependiente es la función que buscas (y). La independiente es respecto a la que derivamos (x).",
                "explicacion": "Variable dependiente: y (la función que buscamos). Variable independiente: x (respecto a la cual derivamos).",
                "respuestas_correctas": [
                    "dependiente y, independiente x",
                    "variable dependiente y, variable independiente x",
                    "y dependiente x independiente",
                    "y es la dependiente y x la independiente",
                    "dependiente: y; independiente: x",
                ],
            },
            {
                "id": 2,
                "titulo": "Determinar el Orden",
                "xp_base": 20,
                "tiempo_limite_segundos": 120,
                "nivel_nombre": "Principiante",
                "nivel_color": "#22c55e",
                "nivel_icono": "🌱",
                "completado": False,
                "intentos": 0,
                "tipo_respuesta": "texto",
                "problema": "Clasifica el orden de la ecuación d^2y/dx^2 + 3 dy/dx + y = 0.",
                "ecuacion_latex": r"\\frac{d^2 y}{dx^2} + 3 \\frac{dy}{dx} + y = 0",
                "pista": "El orden lo marca la mayor derivada presente.",
                "explicacion": "Es de segundo orden porque la derivada de mayor grado es d^2y/dx^2.",
                "respuestas_correctas": [
                    "segundo orden",
                    "orden 2",
                    "2",
                ],
            },
            {
                "id": 3,
                "titulo": "Lineal vs No Lineal",
                "xp_base": 25,
                "tiempo_limite_segundos": 120,
                "nivel_nombre": "Básico",
                "nivel_color": "#3b82f6",
                "nivel_icono": "⭐",
                "completado": False,
                "intentos": 0,
                "tipo_respuesta": "opcion_multiple",
                "problema": "Indica si la ecuación y' + y^2 = x es lineal.",
                "pista": "Una EDO lineal no tiene potencias de la función mayores a 1 ni productos de la función consigo misma.",
                "explicacion": "No es lineal porque aparece y^2 (potencia mayor que 1 de la función).",
                "opciones": ["Lineal", "No lineal"],
                "respuestas_correctas": ["No lineal"],
            },
        ]
        self._display_exercises(mock_exercises)
    
    def _display_exercises(self, exercises: list):
        """Muestra los ejercicios en la lista."""
        self.all_exercises = exercises
        
        completed = sum(1 for e in exercises if e.get('completado', False))
        self.category_progress_label.setText(f"{completed}/{len(exercises)} completados")
        
        for exercise in exercises:
            card = ExerciseCard(exercise)
            card.clicked.connect(self._on_exercise_clicked)
            self.exercises_list_layout.addWidget(card)
        
        self.exercises_list_layout.addStretch()
    
    def _filter_exercises(self, nivel_id: int):
        """Filtra ejercicios por nivel."""
        # Actualizar botones
        for btn in self.filter_buttons:
            btn_level = btn.property("nivel_id")
            btn.setChecked(btn_level == nivel_id if nivel_id is not None else btn_level is None)
        
        # Filtrar y mostrar
        if nivel_id is None:
            filtered = self.all_exercises
        else:
            filtered = [e for e in self.all_exercises if e.get('nivel_id') == nivel_id]
        
        # Limpiar y mostrar
        while self.exercises_list_layout.count():
            item = self.exercises_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        for exercise in filtered:
            card = ExerciseCard(exercise)
            card.clicked.connect(self._on_exercise_clicked)
            self.exercises_list_layout.addWidget(card)
        
        self.exercises_list_layout.addStretch()
    
    def _on_exercise_clicked(self, exercise_data: dict):
        """Abre el diálogo de ejercicio."""
        # Añadir info de categoría si falta
        if self.current_category:
            exercise_data['categoria_nombre'] = self.current_category.get('nombre', '')
        
        dialog = ExerciseDialog(exercise_data, self)
        dialog.exercise_completed.connect(self._on_exercise_completed)
        dialog.exec()
    
    def _on_exercise_completed(self, result: dict):
        """Maneja la finalización de un ejercicio."""
        if result.get('is_correct') and self.db and self.user_id:
            try:
                self.db.submit_exercise_answer(
                    self.user_id,
                    result['exercise_id'],
                    "",  # respuesta no necesaria porque ya fue validada
                    result.get('time_seconds'),
                    is_validated=True,
                    xp_override=result.get('xp_earned'),
                    attempts=result.get('attempts')
                )
            except Exception as e:
                print(f"Error guardando resultado: {e}")
        
        # Recargar ejercicios
        if self.current_category:
            self._load_exercises(self.current_category['id'])

        # Disparar señal para que vistas de progreso se refresquen
        if result.get('is_correct'):
            self.exercise_completed.emit(result)
    
    def _back_to_categories(self):
        """Vuelve a la vista de categorías."""
        self.stack.setCurrentIndex(0)
        self._load_data()  # Recargar para actualizar progreso
