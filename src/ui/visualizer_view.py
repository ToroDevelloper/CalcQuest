from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt

class VisualizerView(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Header
        header = QLabel("Laboratorio Visual")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e293b; margin-bottom: 10px;")
        layout.addWidget(header)
        
        sub_header = QLabel("Juega con los parámetros para entender el comportamiento.")
        sub_header.setStyleSheet("font-size: 16px; color: #64748b; margin-bottom: 30px;")
        layout.addWidget(sub_header)
        
        # Visualization Container (Placeholder for Matplotlib/Manim later)
        # For now, mocking the SVG/Canvas area from mockup
        vis_container = QFrame()
        vis_container.setStyleSheet("background-color: white; border-radius: 30px; border: 1px solid #e2e8f0;")
        vis_layout = QVBoxLayout(vis_container)
        vis_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        placeholder_text = QLabel("Espacio para Gráfica Interactiva (Matplotlib/Manim)")
        placeholder_text.setStyleSheet("color: #94a3b8; font-size: 18px; font-weight: bold;")
        vis_layout.addWidget(placeholder_text)
        
        # Mock Curve Description
        curve_desc = QLabel("Familia de Curvas: y = Ce^(-2x)")
        curve_desc.setStyleSheet("color: #6366f1; font-size: 20px; font-weight: bold; margin-top: 20px;")
        vis_layout.addWidget(curve_desc)
        
        layout.addWidget(vis_container, stretch=1)
        
        # Controls Section
        controls_container = QFrame()
        controls_container.setStyleSheet("background-color: #f8fafc; border-radius: 16px; padding: 20px; margin-top: 20px;")
        controls_layout = QVBoxLayout(controls_container)
        
        # Constant C Control
        c_label_layout = QHBoxLayout()
        c_label = QLabel("Constante C")
        c_label.setStyleSheet("font-weight: bold; color: #1e293b;")
        self.c_value_label = QLabel("2.5")
        self.c_value_label.setStyleSheet("color: #1e293b;")
        
        c_label_layout.addWidget(c_label)
        c_label_layout.addStretch()
        c_label_layout.addWidget(self.c_value_label)
        controls_layout.addLayout(c_label_layout)
        
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(25)
        self.slider.valueChanged.connect(self._update_value)
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #cbd5e1;
                height: 8px;
                background: white;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #ec4899;
                border: 1px solid #ec4899;
                width: 18px;
                height: 18px;
                margin: -7px 0;
                border-radius: 9px;
            }
        """)
        controls_layout.addWidget(self.slider)
        
        hint = QLabel("Desliza para ver cómo la constante de integración afecta a la familia de curvas.")
        hint.setStyleSheet("margin-top: 10px; font-size: 13px; color: #64748b;")
        controls_layout.addWidget(hint)
        
        layout.addWidget(controls_container)

    def _update_value(self, value):
        real_value = value / 10.0
        self.c_value_label.setText(f"{real_value:.1f}")