from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QPushButton, QLineEdit, QTextEdit,
    QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, QFrame,
    QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QImage
import io

# Intentar importar matplotlib para renderizado LaTeX
try:
    import matplotlib
    matplotlib.use('Agg')  # Backend sin GUI para renderizado
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class MathSymbolButton(QPushButton):
    """
    Botón personalizado para símbolos matemáticos con soporte de tooltip.
    """
    def __init__(self, label: str, value: str, tooltip: str = "", parent=None):
        super().__init__(label, parent)
        self.value = value
        self.setToolTip(tooltip if tooltip else label)
        self._apply_style()
    
    def _apply_style(self):
        self.setStyleSheet("""
            QPushButton {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 600;
                color: #334155;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: #e0e7ff;
                border-color: #6366f1;
                color: #4f46e5;
            }
            QPushButton:pressed {
                background-color: #c7d2fe;
            }
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumSize(55, 40)
        self.setMaximumSize(80, 50)


class MathKeyboard(QWidget):
    """
    Widget de teclado virtual matemático para entrada de Ecuaciones Diferenciales.
    
    Características:
    - Símbolos organizados por categorías en pestañas
    - Soporte para QLineEdit y QTextEdit
    - Inserción en posición del cursor
    - Señales para notificar inserciones
    
    Categorías de símbolos:
    - Derivadas: dy/dx, d²y/dx², ∂, y', y'', ẏ, ÿ
    - Operadores: ∫, ∬, ∑, ∏, √, ∛, ±, ∓, ×, ÷
    - Letras Griegas: α, β, γ, δ, ε, θ, λ, μ, π, σ, φ, ω
    - Relaciones: =, ≠, <, >, ≤, ≥, ≈, ∝, →, ⇒
    - Conjuntos/Especiales: ∞, ℕ, ℤ, ℚ, ℝ, ℂ, ∈, ∉, ∅
    """
    
    # Señal emitida cuando se inserta un símbolo (symbol_value, symbol_label)
    symbol_inserted = pyqtSignal(str, str)
    
    def __init__(self, target_input=None, parent=None):
        super().__init__(parent)
        self.target_input = target_input
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz del teclado matemático."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Título del widget
        header = QLabel("⌨ Teclado Matemático")
        header.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #4f46e5;
            padding: 5px;
            background-color: #eef2ff;
            border-radius: 6px;
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)
        
        # Widget de pestañas para categorías
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background-color: #ffffff;
            }
            QTabBar::tab {
                background-color: #f1f5f9;
                border: 1px solid #e2e8f0;
                padding: 6px 12px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 12px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom-color: #ffffff;
                color: #4f46e5;
                font-weight: bold;
            }
            QTabBar::tab:hover:!selected {
                background-color: #e0e7ff;
            }
        """)
        
        # Crear pestañas con símbolos
        self._create_derivatives_tab()
        self._create_operators_tab()
        self._create_greek_tab()
        self._create_relations_tab()
        self._create_special_tab()
        
        main_layout.addWidget(self.tab_widget)
        
        # Área de acceso rápido (símbolos más usados)
        self._create_quick_access(main_layout)
    
    def _create_symbol_grid(self, symbols: list, columns: int = 4) -> QWidget:
        """
        Crea un widget con una cuadrícula de botones de símbolos.
        
        Args:
            symbols: Lista de tuplas (label, value, tooltip)
            columns: Número de columnas en la cuadrícula
        
        Returns:
            QWidget con la cuadrícula de símbolos
        """
        container = QWidget()
        layout = QGridLayout(container)
        layout.setSpacing(6)
        layout.setContentsMargins(8, 8, 8, 8)
        
        row, col = 0, 0
        for symbol_data in symbols:
            if len(symbol_data) == 3:
                label, value, tooltip = symbol_data
            else:
                label, value = symbol_data
                tooltip = ""
            
            btn = MathSymbolButton(label, value, tooltip)
            btn.clicked.connect(lambda checked, v=value, l=label: self._on_symbol_clicked(v, l))
            layout.addWidget(btn, row, col)
            
            col += 1
            if col >= columns:
                col = 0
                row += 1
        
        # Añadir stretch al final para compactar
        layout.setRowStretch(row + 1, 1)
        
        return container
    
    def _create_derivatives_tab(self):
        """Crea la pestaña de símbolos de derivadas."""
        symbols = [
            # Derivadas ordinarias
            ("y'", "y'", "Derivada primera (notación prima)"),
            ("y''", "y''", "Derivada segunda (notación prima)"),
            ("y'''", "y'''", "Derivada tercera (notación prima)"),
            ("ẏ", "ẏ", "Derivada respecto al tiempo (Newton)"),
            ("ÿ", "ÿ", "Derivada segunda temporal (Newton)"),
            
            # Notación de Leibniz
            ("dy/dx", "dy/dx", "Derivada de y respecto a x"),
            ("dx/dt", "dx/dt", "Derivada de x respecto a t"),
            ("d²y/dx²", "d²y/dx²", "Derivada segunda"),
            ("d³y/dx³", "d³y/dx³", "Derivada tercera"),
            ("dⁿy/dxⁿ", "dⁿy/dxⁿ", "Derivada de orden n"),
            
            # Derivadas parciales
            ("∂", "∂", "Derivada parcial"),
            ("∂y/∂x", "∂y/∂x", "Derivada parcial de y respecto a x"),
            ("∂²/∂x²", "∂²/∂x²", "Derivada parcial segunda"),
            ("∂²/∂x∂y", "∂²/∂x∂y", "Derivada parcial mixta"),
            
            # Operadores diferenciales
            ("∇", "∇", "Operador nabla (gradiente)"),
            ("∇²", "∇²", "Laplaciano"),
            ("Δ", "Δ", "Delta (Laplaciano)"),
            ("D", "D", "Operador diferencial D"),
        ]
        
        tab = self._create_symbol_grid(symbols, columns=4)
        scroll = QScrollArea()
        scroll.setWidget(tab)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.tab_widget.addTab(scroll, "∂ Derivadas")
    
    def _create_operators_tab(self):
        """Crea la pestaña de operadores matemáticos."""
        symbols = [
            # Integrales
            ("∫", "∫", "Integral"),
            ("∬", "∬", "Integral doble"),
            ("∭", "∭", "Integral triple"),
            ("∮", "∮", "Integral de línea cerrada"),
            
            # Sumatorias y productos
            ("∑", "∑", "Sumatoria"),
            ("∏", "∏", "Productoria"),
            
            # Raíces
            ("√", "√", "Raíz cuadrada"),
            ("∛", "∛", "Raíz cúbica"),
            ("ⁿ√", "ⁿ√", "Raíz n-ésima"),
            
            # Operadores básicos
            ("±", "±", "Más menos"),
            ("∓", "∓", "Menos más"),
            ("×", "×", "Multiplicación"),
            ("÷", "÷", "División"),
            ("·", "·", "Producto punto"),
            
            # Exponentes y subíndices
            ("^", "^", "Exponente"),
            ("_", "_", "Subíndice"),
            ("²", "²", "Al cuadrado"),
            ("³", "³", "Al cubo"),
            ("ⁿ", "ⁿ", "A la n"),
            
            # Funciones especiales
            ("eˣ", "e^x", "Exponencial"),
            ("ln", "ln", "Logaritmo natural"),
            ("log", "log", "Logaritmo"),
            ("|x|", "|x|", "Valor absoluto"),
        ]
        
        tab = self._create_symbol_grid(symbols, columns=4)
        scroll = QScrollArea()
        scroll.setWidget(tab)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.tab_widget.addTab(scroll, "∫ Operadores")
    
    def _create_greek_tab(self):
        """Crea la pestaña de letras griegas."""
        symbols = [
            # Minúsculas comunes en EDOs
            ("α", "α", "Alpha"),
            ("β", "β", "Beta"),
            ("γ", "γ", "Gamma"),
            ("δ", "δ", "Delta"),
            ("ε", "ε", "Epsilon"),
            ("ζ", "ζ", "Zeta"),
            ("η", "η", "Eta"),
            ("θ", "θ", "Theta"),
            ("ι", "ι", "Iota"),
            ("κ", "κ", "Kappa"),
            ("λ", "λ", "Lambda"),
            ("μ", "μ", "Mu"),
            ("ν", "ν", "Nu"),
            ("ξ", "ξ", "Xi"),
            ("π", "π", "Pi"),
            ("ρ", "ρ", "Rho"),
            ("σ", "σ", "Sigma"),
            ("τ", "τ", "Tau"),
            ("υ", "υ", "Upsilon"),
            ("φ", "φ", "Phi"),
            ("χ", "χ", "Chi"),
            ("ψ", "ψ", "Psi"),
            ("ω", "ω", "Omega"),
            
            # Mayúsculas importantes
            ("Γ", "Γ", "Gamma mayúscula"),
            ("Δ", "Δ", "Delta mayúscula"),
            ("Θ", "Θ", "Theta mayúscula"),
            ("Λ", "Λ", "Lambda mayúscula"),
            ("Σ", "Σ", "Sigma mayúscula"),
            ("Φ", "Φ", "Phi mayúscula"),
            ("Ψ", "Ψ", "Psi mayúscula"),
            ("Ω", "Ω", "Omega mayúscula"),
        ]
        
        tab = self._create_symbol_grid(symbols, columns=5)
        scroll = QScrollArea()
        scroll.setWidget(tab)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.tab_widget.addTab(scroll, "α Griegas")
    
    def _create_relations_tab(self):
        """Crea la pestaña de relaciones y comparaciones."""
        symbols = [
            # Igualdad y desigualdad
            ("=", "=", "Igual"),
            ("≠", "≠", "No igual"),
            ("≈", "≈", "Aproximadamente igual"),
            ("≡", "≡", "Idéntico/Congruente"),
            ("≢", "≢", "No idéntico"),
            
            # Comparaciones
            ("<", "<", "Menor que"),
            (">", ">", "Mayor que"),
            ("≤", "≤", "Menor o igual"),
            ("≥", "≥", "Mayor o igual"),
            ("≪", "≪", "Mucho menor que"),
            ("≫", "≫", "Mucho mayor que"),
            
            # Proporcionalidad
            ("∝", "∝", "Proporcional a"),
            ("∼", "∼", "Similar a"),
            
            # Flechas
            ("→", "→", "Tiende a / Implica"),
            ("←", "←", "Flecha izquierda"),
            ("↔", "↔", "Si y solo si"),
            ("⇒", "⇒", "Implica (doble)"),
            ("⇐", "⇐", "Implica inverso"),
            ("⇔", "⇔", "Equivalente"),
            ("↦", "↦", "Mapea a"),
            
            # Límites
            ("lim", "lim", "Límite"),
            ("x→∞", "x→∞", "x tiende a infinito"),
            ("x→0", "x→0", "x tiende a cero"),
            ("x→0⁺", "x→0⁺", "x tiende a 0 por derecha"),
            ("x→0⁻", "x→0⁻", "x tiende a 0 por izquierda"),
        ]
        
        tab = self._create_symbol_grid(symbols, columns=5)
        scroll = QScrollArea()
        scroll.setWidget(tab)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.tab_widget.addTab(scroll, "≤ Relaciones")
    
    def _create_special_tab(self):
        """Crea la pestaña de símbolos especiales y constantes."""
        symbols = [
            # Infinito y constantes
            ("∞", "∞", "Infinito"),
            ("-∞", "-∞", "Infinito negativo"),
            ("e", "e", "Número de Euler"),
            ("i", "i", "Unidad imaginaria"),
            ("π", "π", "Pi"),
            
            # Conjuntos numéricos
            ("ℕ", "ℕ", "Números naturales"),
            ("ℤ", "ℤ", "Números enteros"),
            ("ℚ", "ℚ", "Números racionales"),
            ("ℝ", "ℝ", "Números reales"),
            ("ℂ", "ℂ", "Números complejos"),
            
            # Pertenencia
            ("∈", "∈", "Pertenece a"),
            ("∉", "∉", "No pertenece a"),
            ("⊂", "⊂", "Subconjunto"),
            ("⊃", "⊃", "Superconjunto"),
            ("∅", "∅", "Conjunto vacío"),
            
            # Lógica
            ("∀", "∀", "Para todo"),
            ("∃", "∃", "Existe"),
            ("∄", "∄", "No existe"),
            ("∧", "∧", "Y lógico"),
            ("∨", "∨", "O lógico"),
            ("¬", "¬", "Negación"),
            
            # Funciones trigonométricas
            ("sin", "sin", "Seno"),
            ("cos", "cos", "Coseno"),
            ("tan", "tan", "Tangente"),
            ("sec", "sec", "Secante"),
            ("csc", "csc", "Cosecante"),
            ("cot", "cot", "Cotangente"),
            
            # Paréntesis especiales
            ("(", "(", "Paréntesis izquierdo"),
            (")", ")", "Paréntesis derecho"),
            ("[", "[", "Corchete izquierdo"),
            ("]", "]", "Corchete derecho"),
            ("{", "{", "Llave izquierda"),
            ("}", "}", "Llave derecha"),
        ]
        
        tab = self._create_symbol_grid(symbols, columns=5)
        scroll = QScrollArea()
        scroll.setWidget(tab)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.tab_widget.addTab(scroll, "∞ Especiales")
    
    def _create_quick_access(self, parent_layout: QVBoxLayout):
        """Crea la barra de acceso rápido con los símbolos más usados."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #f0fdf4;
                border: 1px solid #bbf7d0;
                border-radius: 8px;
            }
        """)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)
        
        # Label
        label = QLabel("Rápido:")
        label.setStyleSheet("font-size: 11px; font-weight: bold; color: #166534;")
        layout.addWidget(label)
        
        # Símbolos más usados en EDOs
        quick_symbols = [
            ("y'", "y'", "Derivada primera"),
            ("dy/dx", "dy/dx", "Derivada"),
            ("∫", "∫", "Integral"),
            ("e^x", "e^x", "Exponencial"),
            ("λ", "λ", "Lambda"),
            ("∞", "∞", "Infinito"),
            ("=", "=", "Igual"),
            ("±", "±", "Más menos"),
        ]
        
        for label_text, value, tooltip in quick_symbols:
            btn = QPushButton(label_text)
            btn.setToolTip(tooltip)
            btn.setFixedSize(45, 30)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #dcfce7;
                    border: 1px solid #86efac;
                    border-radius: 5px;
                    font-size: 12px;
                    font-weight: bold;
                    color: #166534;
                }
                QPushButton:hover {
                    background-color: #bbf7d0;
                    border-color: #22c55e;
                }
                QPushButton:pressed {
                    background-color: #86efac;
                }
            """)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, v=value, l=label_text: self._on_symbol_clicked(v, l))
            layout.addWidget(btn)
        
        layout.addStretch()
        parent_layout.addWidget(frame)
    
    def _on_symbol_clicked(self, value: str, label: str):
        """Maneja el clic en un botón de símbolo."""
        self._insert_symbol(value)
        self.symbol_inserted.emit(value, label)
    
    def set_target_input(self, widget):
        """
        Establece el widget de entrada donde se insertarán los símbolos.
        
        Args:
            widget: QLineEdit o QTextEdit donde insertar símbolos
        """
        self.target_input = widget
    
    def _insert_symbol(self, symbol: str):
        """
        Inserta el símbolo en el widget objetivo en la posición actual del cursor.
        
        Args:
            symbol: El símbolo a insertar
        """
        if not self.target_input:
            return
        
        # Asegurar que el widget tenga el foco
        self.target_input.setFocus()
        
        if isinstance(self.target_input, QLineEdit):
            # Obtener posición del cursor y texto actual
            cursor_pos = self.target_input.cursorPosition()
            current_text = self.target_input.text()
            
            # Insertar símbolo en la posición del cursor
            new_text = current_text[:cursor_pos] + symbol + current_text[cursor_pos:]
            self.target_input.setText(new_text)
            
            # Mover cursor después del símbolo insertado
            self.target_input.setCursorPosition(cursor_pos + len(symbol))
        
        elif isinstance(self.target_input, QTextEdit):
            # Insertar en la posición del cursor del QTextEdit
            cursor = self.target_input.textCursor()
            cursor.insertText(symbol)
            self.target_input.setTextCursor(cursor)


class MathRenderWidget(QLabel):
    """
    Widget para renderizar y mostrar expresiones matemáticas en formato LaTeX.
    Utiliza matplotlib para convertir LaTeX a imagen.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(50)
        self.setStyleSheet("""
            QLabel {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        self._last_latex = ""
    
    def render_latex(self, latex_expr: str, fontsize: int = 14, dpi: int = 150):
        """
        Renderiza una expresión LaTeX y la muestra como imagen.
        
        Args:
            latex_expr: Expresión en formato LaTeX (sin delimitadores $ $)
            fontsize: Tamaño de fuente para el renderizado
            dpi: Resolución de la imagen generada
        """
        if not MATPLOTLIB_AVAILABLE:
            self.setText(f"[LaTeX]: {latex_expr}")
            return
        
        if not latex_expr or latex_expr == self._last_latex:
            return
        
        self._last_latex = latex_expr
        
        try:
            # Crear figura de matplotlib
            fig = plt.figure(figsize=(8, 1))
            fig.patch.set_facecolor('white')
            
            # Renderizar LaTeX
            fig.text(
                0.5, 0.5,
                f"${latex_expr}$",
                fontsize=fontsize,
                ha='center',
                va='center',
                transform=fig.transFigure
            )
            
            # Convertir a imagen
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=dpi, 
                       bbox_inches='tight', pad_inches=0.1,
                       facecolor='white', edgecolor='none')
            buf.seek(0)
            plt.close(fig)
            
            # Cargar en QPixmap
            image = QImage()
            image.loadFromData(buf.getvalue())
            pixmap = QPixmap.fromImage(image)
            
            # Escalar si es muy grande
            if pixmap.width() > self.width() - 20:
                pixmap = pixmap.scaledToWidth(
                    self.width() - 20,
                    Qt.TransformationMode.SmoothTransformation
                )
            
            self.setPixmap(pixmap)
            
        except Exception as e:
            # Si falla el renderizado, mostrar texto plano
            self.setText(f"[LaTeX]: {latex_expr}")
    
    def clear_render(self):
        """Limpia el renderizado actual."""
        self.clear()
        self._last_latex = ""
    
    def set_plain_text(self, text: str):
        """Muestra texto plano sin renderizado LaTeX."""
        self.setText(text)
        self._last_latex = ""


class MathInputWidget(QWidget):
    """
    Widget combinado que incluye un campo de entrada y el teclado matemático.
    Facilita la integración del teclado con la entrada de texto.
    """
    
    # Señal emitida cuando cambia el texto
    text_changed = pyqtSignal(str)
    # Señal emitida al presionar Enter
    return_pressed = pyqtSignal()
    
    def __init__(self, placeholder: str = "Escribe tu ecuación...", parent=None):
        super().__init__(parent)
        self._setup_ui(placeholder)
    
    def _setup_ui(self, placeholder: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Campo de entrada
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(placeholder)
        self.input_field.setStyleSheet("""
            QLineEdit {
                font-size: 16px;
                padding: 12px 15px;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                background-color: #ffffff;
            }
            QLineEdit:focus {
                border-color: #6366f1;
                background-color: #fafafa;
            }
        """)
        self.input_field.textChanged.connect(self.text_changed.emit)
        self.input_field.returnPressed.connect(self.return_pressed.emit)
        layout.addWidget(self.input_field)
        
        # Teclado matemático
        self.keyboard = MathKeyboard(target_input=self.input_field)
        layout.addWidget(self.keyboard)
    
    def text(self) -> str:
        """Retorna el texto actual del campo de entrada."""
        return self.input_field.text()
    
    def set_text(self, text: str):
        """Establece el texto del campo de entrada."""
        self.input_field.setText(text)
    
    def clear(self):
        """Limpia el campo de entrada."""
        self.input_field.clear()
    
    def get_keyboard(self) -> MathKeyboard:
        """Retorna el widget del teclado matemático."""
        return self.keyboard
    
    def get_input_field(self) -> QLineEdit:
        """Retorna el widget del campo de entrada."""
        return self.input_field