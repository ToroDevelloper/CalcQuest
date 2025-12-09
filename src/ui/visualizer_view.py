from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSlider, QHBoxLayout, QFrame,
    QComboBox, QPushButton, QGridLayout, QSizePolicy, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
import numpy as np
import io

# Importar matplotlib con backend Agg para renderizado sin GUI
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class PlotWidget(QLabel):
    """Widget para mostrar gráficas de matplotlib como QLabel."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(400, 300)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }
        """)
        self._figure = None
        self._dpi = 100
    
    def update_plot(self, figure):
        """Actualiza el widget con una nueva figura de matplotlib."""
        if not MATPLOTLIB_AVAILABLE:
            self.setText("Matplotlib no disponible")
            return
        
        self._figure = figure
        
        # Convertir figura a imagen
        buf = io.BytesIO()
        figure.savefig(buf, format='png', dpi=self._dpi, 
                      bbox_inches='tight', facecolor='white', edgecolor='none')
        buf.seek(0)
        plt.close(figure)
        
        # Cargar en QPixmap
        image = QImage()
        image.loadFromData(buf.getvalue())
        pixmap = QPixmap.fromImage(image)
        
        # Escalar al tamaño del widget manteniendo proporción
        scaled_pixmap = pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled_pixmap)
    
    def resizeEvent(self, event):
        """Reescalar la imagen cuando cambia el tamaño del widget."""
        super().resizeEvent(event)
        if self._figure:
            # Re-renderizar con el nuevo tamaño
            pass  # Por ahora solo escala la imagen existente


class VisualizerView(QWidget):
    """
    Vista del Laboratorio Visual para explorar familias de curvas
    y comportamiento de soluciones de ecuaciones diferenciales.
    """
    
    def __init__(self):
        super().__init__()
        self._current_equation = "exponential_decay"
        self._setup_ui()
        self._update_plot()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ec4899, stop:1 #8b5cf6);
                border-radius: 16px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(25, 20, 25, 20)
        
        header = QLabel("🔬 Laboratorio Visual")
        header.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: white;
        """)
        header_layout.addWidget(header)
        
        sub_header = QLabel("Explora cómo los parámetros afectan las soluciones de ecuaciones diferenciales")
        sub_header.setStyleSheet("font-size: 14px; color: rgba(255,255,255,0.9);")
        header_layout.addWidget(sub_header)
        
        layout.addWidget(header_frame)
        
        # Selector de ecuación
        selector_frame = QFrame()
        selector_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        selector_layout = QHBoxLayout(selector_frame)
        selector_layout.setContentsMargins(15, 10, 15, 10)
        
        selector_label = QLabel("📊 Tipo de Ecuación:")
        selector_label.setStyleSheet("font-weight: bold; color: #334155;")
        selector_layout.addWidget(selector_label)
        
        self.equation_selector = QComboBox()
        self.equation_selector.addItems([
            "Decaimiento Exponencial: y' = -ky",
            "Crecimiento Exponencial: y' = ky",
            "Ecuación Logística: y' = ry(1 - y/K)",
            "Oscilador Armónico: y'' + ω²y = 0",
            "Lineal de Primer Orden: y' + 2y = e^x"
        ])
        self.equation_selector.setStyleSheet("""
            QComboBox {
                padding: 8px 15px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                background-color: white;
                min-width: 300px;
            }
            QComboBox:hover {
                border-color: #6366f1;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
        """)
        self.equation_selector.currentIndexChanged.connect(self._on_equation_changed)
        selector_layout.addWidget(self.equation_selector)
        selector_layout.addStretch()
        
        layout.addWidget(selector_frame)
        
        # Área principal: Gráfica + Controles
        main_content = QHBoxLayout()
        main_content.setSpacing(15)
        
        # Área de gráfica
        self.plot_widget = PlotWidget()
        main_content.addWidget(self.plot_widget, stretch=2)
        
        # Panel de controles
        controls_frame = QFrame()
        controls_frame.setFixedWidth(280)
        controls_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }
        """)
        controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setContentsMargins(20, 20, 20, 20)
        controls_layout.setSpacing(20)
        
        # Título de controles
        controls_title = QLabel("⚙️ Parámetros")
        controls_title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #1e293b;
            padding-bottom: 10px;
            border-bottom: 2px solid #e2e8f0;
        """)
        controls_layout.addWidget(controls_title)
        
        # Control: Constante C
        self._add_slider_control(
            controls_layout,
            "Constante C",
            "Constante de integración",
            -50, 50, 25,
            self._on_c_changed,
            "c_slider",
            "c_value_label"
        )
        
        # Control: Parámetro k
        self._add_slider_control(
            controls_layout,
            "Parámetro k",
            "Tasa de cambio",
            1, 50, 20,
            self._on_k_changed,
            "k_slider",
            "k_value_label"
        )
        
        # Control: Rango de t
        self._add_slider_control(
            controls_layout,
            "Rango de t",
            "Intervalo de tiempo",
            10, 100, 50,
            self._on_range_changed,
            "range_slider",
            "range_value_label"
        )
        
        # Control: Número de curvas
        self._add_slider_control(
            controls_layout,
            "Curvas a mostrar",
            "Familia de soluciones",
            1, 10, 5,
            self._on_curves_changed,
            "curves_slider",
            "curves_value_label"
        )
        
        controls_layout.addStretch()
        
        # Botón de reset
        reset_btn = QPushButton("🔄 Restablecer")
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                color: #334155;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        reset_btn.clicked.connect(self._reset_controls)
        controls_layout.addWidget(reset_btn)
        
        main_content.addWidget(controls_frame)
        layout.addLayout(main_content, stretch=1)
        
        # Información de la ecuación actual
        self.info_frame = QFrame()
        self.info_frame.setStyleSheet("""
            QFrame {
                background-color: #eef2ff;
                border-radius: 12px;
                border: 1px solid #c7d2fe;
            }
        """)
        info_layout = QVBoxLayout(self.info_frame)
        info_layout.setContentsMargins(20, 15, 20, 15)
        
        self.equation_label = QLabel("📐 Ecuación: y' = -ky")
        self.equation_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4f46e5;")
        info_layout.addWidget(self.equation_label)
        
        self.solution_label = QLabel("✨ Solución General: y = Ce^(-kx)")
        self.solution_label.setStyleSheet("font-size: 14px; color: #6366f1;")
        info_layout.addWidget(self.solution_label)
        
        self.description_label = QLabel(
            "💡 Esta ecuación modela el decaimiento exponencial, común en desintegración radiactiva, "
            "enfriamiento de objetos y descarga de capacitores."
        )
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("font-size: 13px; color: #64748b; margin-top: 5px;")
        info_layout.addWidget(self.description_label)
        
        layout.addWidget(self.info_frame)
        
        # Inicializar valores
        self._c_value = 2.5
        self._k_value = 2.0
        self._range_value = 5.0
        self._num_curves = 5
    
    def _add_slider_control(self, layout, title, subtitle, min_val, max_val, default, 
                           callback, slider_name, label_name):
        """Añade un control de slider con etiquetas."""
        container = QFrame()
        container.setStyleSheet("background-color: #f8fafc; border-radius: 8px; padding: 5px;")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(10, 8, 10, 8)
        container_layout.setSpacing(5)
        
        # Header del control
        header_layout = QHBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; color: #334155; font-size: 13px;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        value_label = QLabel(f"{default / 10:.1f}")
        value_label.setStyleSheet("color: #6366f1; font-weight: bold; font-size: 13px;")
        setattr(self, label_name, value_label)
        header_layout.addWidget(value_label)
        
        container_layout.addLayout(header_layout)
        
        # Subtitle
        sub_label = QLabel(subtitle)
        sub_label.setStyleSheet("color: #94a3b8; font-size: 11px;")
        container_layout.addWidget(sub_label)
        
        # Slider
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default)
        slider.valueChanged.connect(callback)
        slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #e2e8f0;
                height: 6px;
                background: white;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #6366f1;
                border: 2px solid #4f46e5;
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #4f46e5;
            }
            QSlider::sub-page:horizontal {
                background: #c7d2fe;
                border-radius: 3px;
            }
        """)
        setattr(self, slider_name, slider)
        container_layout.addWidget(slider)
        
        layout.addWidget(container)
    
    def _on_equation_changed(self, index):
        """Maneja el cambio de tipo de ecuación."""
        equations = [
            "exponential_decay",
            "exponential_growth", 
            "logistic",
            "harmonic_oscillator",
            "linear_first_order"
        ]
        self._current_equation = equations[index]
        self._update_info_panel()
        self._update_plot()
    
    def _on_c_changed(self, value):
        self._c_value = value / 10.0
        self.c_value_label.setText(f"{self._c_value:.1f}")
        self._update_plot()
    
    def _on_k_changed(self, value):
        self._k_value = value / 10.0
        self.k_value_label.setText(f"{self._k_value:.1f}")
        self._update_plot()
    
    def _on_range_changed(self, value):
        self._range_value = value / 10.0
        self.range_value_label.setText(f"{self._range_value:.1f}")
        self._update_plot()
    
    def _on_curves_changed(self, value):
        self._num_curves = value
        self.curves_value_label.setText(f"{value}")
        self._update_plot()
    
    def _reset_controls(self):
        """Restablece todos los controles a valores por defecto."""
        self.c_slider.setValue(25)
        self.k_slider.setValue(20)
        self.range_slider.setValue(50)
        self.curves_slider.setValue(5)
    
    def _update_info_panel(self):
        """Actualiza el panel de información según la ecuación seleccionada."""
        info = {
            "exponential_decay": {
                "equation": "y' = -ky",
                "solution": "y = Ce^(-kx)",
                "description": "Modela el decaimiento exponencial: desintegración radiactiva, enfriamiento de Newton, descarga de capacitores."
            },
            "exponential_growth": {
                "equation": "y' = ky",
                "solution": "y = Ce^(kx)",
                "description": "Modela el crecimiento exponencial: poblaciones sin restricciones, interés compuesto continuo."
            },
            "logistic": {
                "equation": "y' = ry(1 - y/K)",
                "solution": "y = K / (1 + Ae^(-rt))",
                "description": "Modela crecimiento con capacidad de carga: poblaciones con recursos limitados, propagación de enfermedades."
            },
            "harmonic_oscillator": {
                "equation": "y'' + ω²y = 0",
                "solution": "y = A·cos(ωx) + B·sin(ωx)",
                "description": "Modela oscilaciones armónicas: péndulos, resortes, circuitos LC."
            },
            "linear_first_order": {
                "equation": "y' + 2y = e^x",
                "solution": "y = (e^x)/3 + Ce^(-2x)",
                "description": "Ecuación lineal de primer orden resuelta con factor integrante."
            }
        }
        
        data = info.get(self._current_equation, info["exponential_decay"])
        self.equation_label.setText(f"📐 Ecuación: {data['equation']}")
        self.solution_label.setText(f"✨ Solución General: {data['solution']}")
        self.description_label.setText(f"💡 {data['description']}")
    
    def _update_plot(self):
        """Actualiza la gráfica según los parámetros actuales."""
        if not MATPLOTLIB_AVAILABLE:
            self.plot_widget.setText("Matplotlib no está disponible.\nInstala con: pip install matplotlib")
            return
        
        # Crear figura
        fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
        fig.patch.set_facecolor('white')
        
        # Configurar estilo
        ax.set_facecolor('#fafafa')
        ax.grid(True, linestyle='--', alpha=0.7, color='#e2e8f0')
        ax.axhline(y=0, color='#94a3b8', linewidth=0.8)
        ax.axvline(x=0, color='#94a3b8', linewidth=0.8)
        
        # Generar datos según el tipo de ecuación
        x = np.linspace(0, self._range_value, 500)
        
        # Colores para las curvas
        colors = plt.cm.viridis(np.linspace(0.2, 0.8, self._num_curves))
        
        # Generar curvas con diferentes valores de C
        c_values = np.linspace(-self._c_value * 2, self._c_value * 2, self._num_curves)
        
        if self._current_equation == "exponential_decay":
            ax.set_title("Familia de Curvas: Decaimiento Exponencial", fontsize=14, fontweight='bold', color='#1e293b')
            ax.set_xlabel("x (tiempo)", fontsize=11, color='#64748b')
            ax.set_ylabel("y (cantidad)", fontsize=11, color='#64748b')
            
            for i, c in enumerate(c_values):
                if c != 0:
                    y = c * np.exp(-self._k_value * x)
                    ax.plot(x, y, color=colors[i], linewidth=2, label=f'C = {c:.1f}')
        
        elif self._current_equation == "exponential_growth":
            ax.set_title("Familia de Curvas: Crecimiento Exponencial", fontsize=14, fontweight='bold', color='#1e293b')
            ax.set_xlabel("x (tiempo)", fontsize=11, color='#64748b')
            ax.set_ylabel("y (cantidad)", fontsize=11, color='#64748b')
            
            for i, c in enumerate(c_values):
                if c != 0:
                    y = c * np.exp(self._k_value * x)
                    # Limitar valores extremos para visualización
                    y = np.clip(y, -100, 100)
                    ax.plot(x, y, color=colors[i], linewidth=2, label=f'C = {c:.1f}')
            ax.set_ylim(-50, 50)
        
        elif self._current_equation == "logistic":
            ax.set_title("Ecuación Logística", fontsize=14, fontweight='bold', color='#1e293b')
            ax.set_xlabel("t (tiempo)", fontsize=11, color='#64748b')
            ax.set_ylabel("P (población)", fontsize=11, color='#64748b')
            
            K = 10  # Capacidad de carga
            r = self._k_value
            
            for i, A in enumerate(np.linspace(0.5, 5, self._num_curves)):
                y = K / (1 + A * np.exp(-r * x))
                ax.plot(x, y, color=colors[i], linewidth=2, label=f'A = {A:.1f}')
            
            # Línea de capacidad de carga
            ax.axhline(y=K, color='#ef4444', linestyle='--', linewidth=1.5, label=f'K = {K}')
        
        elif self._current_equation == "harmonic_oscillator":
            ax.set_title("Oscilador Armónico Simple", fontsize=14, fontweight='bold', color='#1e293b')
            ax.set_xlabel("t (tiempo)", fontsize=11, color='#64748b')
            ax.set_ylabel("y (desplazamiento)", fontsize=11, color='#64748b')
            
            omega = self._k_value
            
            for i, (A, phi) in enumerate(zip(
                np.linspace(0.5, self._c_value, self._num_curves),
                np.linspace(0, np.pi, self._num_curves)
            )):
                y = A * np.cos(omega * x + phi)
                ax.plot(x, y, color=colors[i], linewidth=2, label=f'A={A:.1f}, φ={phi:.1f}')
        
        elif self._current_equation == "linear_first_order":
            ax.set_title("EDO Lineal: y' + 2y = e^x", fontsize=14, fontweight='bold', color='#1e293b')
            ax.set_xlabel("x", fontsize=11, color='#64748b')
            ax.set_ylabel("y", fontsize=11, color='#64748b')
            
            for i, c in enumerate(c_values):
                # Solución: y = e^x/3 + C*e^(-2x)
                y = np.exp(x) / 3 + c * np.exp(-2 * x)
                y = np.clip(y, -50, 50)
                ax.plot(x, y, color=colors[i], linewidth=2, label=f'C = {c:.1f}')
            
            # Solución particular
            y_p = np.exp(x) / 3
            ax.plot(x, y_p, color='#ef4444', linewidth=2.5, linestyle='--', label='Particular: e^x/3')
        
        # Leyenda
        ax.legend(loc='upper right', fontsize=9, framealpha=0.9)
        
        # Ajustar márgenes
        plt.tight_layout()
        
        # Actualizar el widget
        self.plot_widget.update_plot(fig)
    
    # Método para compatibilidad con tests existentes
    def _update_value(self, value):
        """Método legacy para compatibilidad."""
        self._on_c_changed(value)