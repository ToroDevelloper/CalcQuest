from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CalcQuest - Tu Aventura Matemática")
        self.resize(1024, 768)
        
        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main Layout (Horizontal: Sidebar | Content)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(250)
        # Style is now handled globally in main.py via QSS
        self.main_layout.addWidget(self.sidebar)
        
        # Content Area (Stacked Widget for different views)
        self.content_area = QStackedWidget()
        self.content_area.setObjectName("content_area")
        self.main_layout.addWidget(self.content_area)
        
        # Initial Placeholder View (Dashboard)
        self.dashboard_view = QLabel("Dashboard - The Hub")
        self.dashboard_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_area.addWidget(self.dashboard_view)
        
        # Setup Sidebar Layout (Mock items)
        self._setup_sidebar()

    def _setup_sidebar(self):
        layout = QVBoxLayout(self.sidebar)
        
        # Logo / Title Area
        logo_label = QLabel("CalcQuest")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("""
            font-size: 24px;
            font-weight: 800;
            padding: 30px 0;
            color: #6366f1;
        """)
        layout.addWidget(logo_label)
        
        # Navigation Buttons
        self.btn_dashboard = QPushButton("Dashboard")
        self.btn_dashboard.setObjectName("btn_dashboard")
        self.btn_dashboard.clicked.connect(lambda: self.content_area.setCurrentIndex(0))
        layout.addWidget(self.btn_dashboard)
        
        self.btn_solver = QPushButton("The Solver")
        self.btn_solver.setObjectName("btn_solver")
        self.btn_solver.clicked.connect(lambda: self.content_area.setCurrentIndex(1))
        layout.addWidget(self.btn_solver)
        
        self.btn_visualizer = QPushButton("Visualizer")
        self.btn_visualizer.setObjectName("btn_visualizer")
        self.btn_visualizer.clicked.connect(lambda: self.content_area.setCurrentIndex(2))
        layout.addWidget(self.btn_visualizer)
        
        layout.addStretch()
