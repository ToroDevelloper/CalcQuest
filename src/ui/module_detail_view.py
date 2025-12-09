from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget,
                             QHBoxLayout, QFrame, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QUrl
from PyQt6.QtGui import QDesktopServices

class ModuleDetailView(QWidget):
    back_requested = pyqtSignal()

    def __init__(self, module_data: dict):
        super().__init__()
        self.module_data = module_data
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Header with Back Button
        header_layout = QHBoxLayout()
        self.back_btn = QPushButton("← Volver")
        self.back_btn.setObjectName("back_btn")
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #64748b;
                border: none;
                font-weight: bold;
                font-size: 16px;
                text-align: left;
            }
            QPushButton:hover {
                color: #3498db;
            }
        """)
        self.back_btn.clicked.connect(self.back_requested.emit)
        header_layout.addWidget(self.back_btn)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Module Title & Description
        self.title_label = QLabel(self.module_data.get("title", "Módulo"))
        self.title_label.setObjectName("module_title")
        self.title_label.setStyleSheet("font-size: 32px; font-weight: 800; color: #1e293b; margin-top: 10px;")
        layout.addWidget(self.title_label)
        
        desc_label = QLabel(self.module_data.get("description", ""))
        desc_label.setStyleSheet("font-size: 18px; color: #64748b; margin-bottom: 20px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Content Layout
        content_layout = QHBoxLayout()
        
        # Left: Resources (Tutorials, Readings)
        resources_frame = QFrame()
        resources_frame.setStyleSheet("background-color: white; border-radius: 16px;")
        res_layout = QVBoxLayout(resources_frame)
        res_layout.addWidget(QLabel("📚 Recursos de Aprendizaje"))
        
        self.resources_list = QListWidget()
        self.resources_list.setObjectName("resources_list")
        self.resources_list.addItems(self.module_data.get("resources", []))
        self.resources_list.itemClicked.connect(self._handle_resource_click)
        res_layout.addWidget(self.resources_list)
        
        content_layout.addWidget(resources_frame)
        
        # Right: Exercises
        exercises_frame = QFrame()
        exercises_frame.setStyleSheet("background-color: white; border-radius: 16px;")
        ex_layout = QVBoxLayout(exercises_frame)
        ex_layout.addWidget(QLabel("✏️ Ejercicios Prácticos"))
        
        self.exercises_list = QListWidget()
        self.exercises_list.setObjectName("exercises_list")
        self.exercises_list.addItems(self.module_data.get("exercises", []))
        self.exercises_list.itemClicked.connect(self._handle_exercise_click)
        ex_layout.addWidget(self.exercises_list)
        
        content_layout.addWidget(exercises_frame)
        
        layout.addLayout(content_layout)
        layout.addStretch()

    def _handle_resource_click(self, item):
        text = item.text()
        if "Video" in text:
            # Video Link Logic
            url = QUrl("https://www.youtube.com/watch?v=U7L2XmS7dl0&t=462s")
            QDesktopServices.openUrl(url)
        elif "Lectura" in text:
            # Reading Logic (Dialog for now)
            QMessageBox.information(self, "Recurso de Lectura",
                "Contenido Educativo:\n\n"
                "Una Ecuación Diferencial Ordinaria (EDO) relaciona una función desconocida de una variable independiente con sus derivadas.\n\n"
                "Orden: La derivada más alta presente en la ecuación.\n"
                "Linealidad: La variable dependiente y sus derivadas aparecen con potencia 1 y no multiplicadas entre sí.")

    def _handle_exercise_click(self, item):
        # Exercise Logic (Dialog showing a problem)
        QMessageBox.information(self, "Ejercicio Práctico",
            f"Problema Seleccionado: {item.text()}\n\n"
            "Instrucciones:\n"
            "Resuelve el problema en tu cuaderno y verifica la solución usando 'The Solver' en el menú lateral.")