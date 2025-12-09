from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QVBoxLayout, 
    QLabel, QPushButton, QFrame, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class SidebarButton(QPushButton):
    """Botón estilizado para el sidebar."""
    
    def __init__(self, text: str, icon: str = "", parent=None):
        super().__init__(f"{icon}  {text}" if icon else text, parent)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 14px 20px;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 500;
                color: #64748b;
                background-color: transparent;
                margin: 2px 10px;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
                color: #1e293b;
            }
            QPushButton:checked {
                background-color: #eef2ff;
                color: #6366f1;
                font-weight: 600;
            }
        """)


class MainWindow(QMainWindow):
    """Ventana principal de CalcQuest con sistema de navegación mejorado."""
    
    def __init__(self, db=None, user_id: int = None):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.nav_buttons = []
        
        self.setWindowTitle("CalcQuest - Aprende Ecuaciones Diferenciales")
        self.resize(1280, 800)
        self.setMinimumSize(1024, 700)
        
        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main Layout (Horizontal: Sidebar | Content)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(260)
        self.sidebar.setStyleSheet("""
            #sidebar {
                background-color: white;
                border-right: 1px solid #e2e8f0;
            }
        """)
        self.main_layout.addWidget(self.sidebar)
        
        # Content Area (Stacked Widget for different views)
        self.content_area = QStackedWidget()
        self.content_area.setObjectName("content_area")
        self.content_area.setStyleSheet("""
            #content_area {
                background-color: #f8fafc;
            }
        """)
        self.main_layout.addWidget(self.content_area)
        
        # Setup UI
        self._setup_sidebar()
        self._setup_views()
        
        # Seleccionar Dashboard por defecto
        self._navigate_to(0)

    def _setup_sidebar(self):
        """Configura el sidebar con navegación mejorada."""
        layout = QVBoxLayout(self.sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header con logo
        header = QFrame()
        header.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #6366f1, stop:1 #8b5cf6);
            padding: 20px;
        """)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(20, 25, 20, 25)
        
        logo_label = QLabel("📐 CalcQuest")
        logo_label.setStyleSheet("""
            font-size: 22px;
            font-weight: 800;
            color: white;
        """)
        header_layout.addWidget(logo_label)
        
        subtitle = QLabel("Ecuaciones Diferenciales")
        subtitle.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.8);")
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header)
        
        # Contenedor de navegación
        nav_container = QWidget()
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(5, 20, 5, 10)
        nav_layout.setSpacing(5)
        
        # Sección: Principal
        section_label = QLabel("PRINCIPAL")
        section_label.setStyleSheet("""
            font-size: 11px;
            font-weight: 600;
            color: #94a3b8;
            padding: 10px 15px 5px 15px;
        """)
        nav_layout.addWidget(section_label)
        
        # Botones de navegación principal
        self.btn_dashboard = SidebarButton("Dashboard", "🏠")
        self.btn_dashboard.setObjectName("btn_dashboard")
        self.btn_dashboard.clicked.connect(lambda: self._navigate_to(0))
        nav_layout.addWidget(self.btn_dashboard)
        self.nav_buttons.append(self.btn_dashboard)
        
        self.btn_exercises = SidebarButton("Ejercicios", "📝")
        self.btn_exercises.setObjectName("btn_exercises")
        self.btn_exercises.clicked.connect(lambda: self._navigate_to(1))
        nav_layout.addWidget(self.btn_exercises)
        self.nav_buttons.append(self.btn_exercises)
        
        self.btn_progress = SidebarButton("Mi Progreso", "📊")
        self.btn_progress.setObjectName("btn_progress")
        self.btn_progress.clicked.connect(lambda: self._navigate_to(2))
        nav_layout.addWidget(self.btn_progress)
        self.nav_buttons.append(self.btn_progress)
        
        # Sección: Herramientas
        section_label2 = QLabel("HERRAMIENTAS")
        section_label2.setStyleSheet("""
            font-size: 11px;
            font-weight: 600;
            color: #94a3b8;
            padding: 20px 15px 5px 15px;
        """)
        nav_layout.addWidget(section_label2)
        
        self.btn_solver = SidebarButton("Solucionador", "🧮")
        self.btn_solver.setObjectName("btn_solver")
        self.btn_solver.clicked.connect(lambda: self._navigate_to(3))
        nav_layout.addWidget(self.btn_solver)
        self.nav_buttons.append(self.btn_solver)
        
        self.btn_visualizer = SidebarButton("Graficador", "📈")
        self.btn_visualizer.setObjectName("btn_visualizer")
        self.btn_visualizer.clicked.connect(lambda: self._navigate_to(4))
        nav_layout.addWidget(self.btn_visualizer)
        self.nav_buttons.append(self.btn_visualizer)
        
        # Sección: Aprendizaje
        section_label3 = QLabel("APRENDIZAJE")
        section_label3.setStyleSheet("""
            font-size: 11px;
            font-weight: 600;
            color: #94a3b8;
            padding: 20px 15px 5px 15px;
        """)
        nav_layout.addWidget(section_label3)
        
        self.btn_theory = SidebarButton("Teoría", "📚")
        self.btn_theory.setObjectName("btn_theory")
        self.btn_theory.clicked.connect(lambda: self._navigate_to(5))
        nav_layout.addWidget(self.btn_theory)
        self.nav_buttons.append(self.btn_theory)
        
        nav_layout.addStretch()
        layout.addWidget(nav_container, stretch=1)
        
        # Footer con info del usuario
        footer = QFrame()
        footer.setStyleSheet("""
            background-color: #f8fafc;
            border-top: 1px solid #e2e8f0;
        """)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(15, 12, 15, 12)
        
        user_info = QVBoxLayout()
        user_name = QLabel("👤 Estudiante")
        user_name.setStyleSheet("font-size: 13px; font-weight: 600; color: #1e293b;")
        user_info.addWidget(user_name)
        
        user_level = QLabel("⭐ Nivel 1")
        user_level.setStyleSheet("font-size: 11px; color: #64748b;")
        user_info.addWidget(user_level)
        
        footer_layout.addLayout(user_info)
        footer_layout.addStretch()
        
        layout.addWidget(footer)
    
    def _setup_views(self):
        """Configura las vistas del contenido."""
        # Importar vistas
        from src.ui.dashboard_view import DashboardView
        from src.ui.exercises_view import ExercisesView
        from src.ui.progress_view import ProgressView
        from src.ui.solver_view import SolverView
        from src.ui.visualizer_view import VisualizerView
        from src.ui.module_detail_view import ModuleDetailView
        
        # 0. Dashboard
        self.dashboard_view = DashboardView()
        self.content_area.addWidget(self.dashboard_view)
        
        # 1. Ejercicios
        self.exercises_view = ExercisesView(db=self.db, user_id=self.user_id)
        self.exercises_view.exercise_completed.connect(self._on_exercise_completed)
        self.content_area.addWidget(self.exercises_view)
        
        # 2. Progreso
        self.progress_view = ProgressView(db=self.db, user_id=self.user_id)
        self.content_area.addWidget(self.progress_view)
        
        # 3. Solucionador
        self.solver_view = SolverView()
        self.content_area.addWidget(self.solver_view)
        
        # 4. Visualizador
        self.visualizer_view = VisualizerView()
        self.content_area.addWidget(self.visualizer_view)
        
        # 5. Teoría (usa ModuleDetailView)
        theory_data = {
            "title": "Fundamentos de Ecuaciones Diferenciales",
            "description": "Aprende los conceptos básicos de las ecuaciones diferenciales, su clasificación y métodos de solución.",
            "resources": [
                "🎥 Video: Introducción a las EDOs",
                "📄 Lectura: Clasificación por Orden y Linealidad",
                "📄 Lectura: Interpretación Geométrica",
                "🎥 Video: Campos de Direcciones"
            ],
            "exercises": [
                "📝 Ejercicio 1: Identificar Variable Dependiente e Independiente",
                "📝 Ejercicio 2: Determinar el Orden de la Ecuación",
                "📝 Ejercicio 3: Verificar si es Lineal o No Lineal"
            ]
        }
        self.theory_view = ModuleDetailView(theory_data)
        self.content_area.addWidget(self.theory_view)

    def _on_exercise_completed(self, result: dict):
        """Refresca vistas de progreso y dashboard tras completar un ejercicio."""
        if hasattr(self, 'progress_view'):
            self.progress_view.refresh()
        if hasattr(self, 'dashboard_view') and hasattr(self.dashboard_view, 'refresh'):
            try:
                self.dashboard_view.refresh()
            except Exception:
                pass
    
    def _navigate_to(self, index: int):
        """Navega a la vista especificada."""
        # Actualizar estado de botones
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        
        # Cambiar vista
        self.content_area.setCurrentIndex(index)
        
        # Refrescar si es necesario
        if index == 2 and hasattr(self, 'progress_view'):
            self.progress_view.refresh()
