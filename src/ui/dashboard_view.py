from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QGridLayout, QFrame, QScrollArea, QPushButton,
                             QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from src.core.gamification import UserProgress

class StatCard(QFrame):
    def __init__(self, icon, value, label, bg_color="#ffffff", icon_bg="#e0e7ff", icon_color="#6366f1"):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 20px;
            }}
        """)
        
        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 10))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Icon
        icon_lbl = QLabel(icon)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet(f"""
            background-color: {icon_bg};
            color: {icon_color};
            border-radius: 12px;
            font-size: 24px;
            padding: 10px;
        """)
        icon_lbl.setFixedSize(50, 50)
        layout.addWidget(icon_lbl)
        
        # Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        value_lbl = QLabel(str(value))
        value_lbl.setStyleSheet("font-size: 24px; font-weight: 800; color: #1e293b;")
        info_layout.addWidget(value_lbl)
        
        label_lbl = QLabel(label)
        label_lbl.setStyleSheet("font-size: 14px; color: #64748b;")
        info_layout.addWidget(label_lbl)
        
        layout.addLayout(info_layout)

class ModuleCard(QFrame):
    clicked = pyqtSignal()

    def __init__(self, icon, title, desc, status, bg_color="white", icon_bg="#fdf2f8", icon_color="#ec4899", status_bg="#ecfdf5", status_color="#10b981", active=True):
        super().__init__()
        self.active = active
        self.setCursor(Qt.CursorShape.PointingHandCursor if active else Qt.CursorShape.ArrowCursor)
        
        style = f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 24px;
                border: 2px solid transparent;
            }}
            QFrame:hover {{
                border: 2px solid #818cf8;
            }}
        """
        if not active:
            style = f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 24px;
                opacity: 0.6;
            }}
            """
            
        self.setStyleSheet(style)
        
        # Shadow
        if active:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)
            shadow.setColor(QColor(0, 0, 0, 15))
            shadow.setOffset(0, 5)
            self.setGraphicsEffect(shadow)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Left Side
        left_layout = QHBoxLayout()
        left_layout.setSpacing(20)
        
        icon_lbl = QLabel(icon)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet(f"""
            background-color: {icon_bg};
            color: {icon_color};
            border-radius: 18px;
            font-size: 24px;
            padding: 10px;
        """)
        icon_lbl.setFixedSize(60, 60)
        left_layout.addWidget(icon_lbl)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 18px; font-weight: 700; color: #1e293b;")
        text_layout.addWidget(title_lbl)
        
        desc_lbl = QLabel(desc)
        desc_lbl.setStyleSheet("font-size: 14px; color: #64748b;")
        text_layout.addWidget(desc_lbl)
        
        left_layout.addLayout(text_layout)
        layout.addLayout(left_layout)
        layout.addStretch()
        
        # Right Side (Status Pill)
        status_lbl = QLabel(status)
        status_lbl.setStyleSheet(f"""
            background-color: {status_bg};
            color: {status_color};
            padding: 6px 14px;
            border-radius: 20px;
            font-weight: 700;
            font-size: 13px;
        """)
        layout.addWidget(status_lbl)

    def mousePressEvent(self, event):
        if self.active:
            self.clicked.emit()
            super().mousePressEvent(event)

class DashboardView(QWidget):
    request_solver = pyqtSignal()
    request_intro = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.user_progress = UserProgress() # Mock
        self.setStyleSheet("background-color: #f0f4f8;")
        self._setup_ui()

    def _setup_ui(self):
        # Main Scroll Area
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")
        
        content_widget = QWidget()
        scroll.setWidget(content_widget)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.addWidget(scroll)

        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # Header
        header_layout = QVBoxLayout()
        welcome_lbl = QLabel("¡Hola, Ángel! 👋")
        welcome_lbl.setObjectName("welcome_label")
        welcome_lbl.setStyleSheet("font-size: 32px; font-weight: 800; color: #1e293b;")
        header_layout.addWidget(welcome_lbl)
        
        sub_lbl = QLabel("Listo para continuar tu racha de aprendizaje?")
        sub_lbl.setStyleSheet("font-size: 18px; color: #64748b; font-weight: 600;")
        header_layout.addWidget(sub_lbl)
        layout.addLayout(header_layout)
        
        # Stats Grid
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        # Streak Card (Mapped from mockup)
        streak_card = StatCard("🔥", f"{self.user_progress.current_streak}", "Días en Racha")
        streak_card.setObjectName("streak_card")
        
        # XP Card
        xp_card = StatCard("💎", f"{self.user_progress.xp}", "Puntos XP", icon_bg="#fce7f3", icon_color="#ec4899")
        xp_card.setObjectName("xp_card")
        
        # Level Card
        level_card = StatCard("🏆", f"Nivel {self.user_progress.level}", "Aprendiz E.D.", icon_bg="#dcfce7", icon_color="#10b981")
        level_card.setObjectName("level_card")

        stats_layout.addWidget(streak_card)
        stats_layout.addWidget(xp_card)
        stats_layout.addWidget(level_card)
        layout.addLayout(stats_layout)
        
        # Learning Path Section
        path_label = QLabel("Tu Ruta de Hoy")
        path_label.setStyleSheet("font-size: 20px; font-weight: 700; color: #1e293b; margin-top: 10px;")
        layout.addWidget(path_label)
        
        path_layout = QVBoxLayout()
        path_layout.setSpacing(20)
        
        # Module 1
        mod1 = ModuleCard("∫", "Introducción a E.D.", "Conceptos básicos y notación", "Completado")
        mod1.clicked.connect(self.request_intro.emit)
        path_layout.addWidget(mod1)
        
        # Module 2 (Active -> Leads to Solver)
        mod2 = ModuleCard("dy", "Variables Separables", "Aprende a dividir y conquistar", "En Progreso", 
                          icon_bg="#e0e7ff", icon_color="#6366f1", status_bg="#e0e7ff", status_color="#6366f1")
        mod2.clicked.connect(self.request_solver.emit)
        path_layout.addWidget(mod2)
        
        # Module 3 (Locked)
        mod3 = ModuleCard("🔒", "Factores Integrantes", "Bloqueado hasta nivel 6", "Bloqueado", 
                          icon_bg="#f1f5f9", icon_color="#94a3b8", status_bg="#f1f5f9", status_color="#94a3b8", active=False)
        path_layout.addWidget(mod3)
        
        layout.addLayout(path_layout)
        layout.addStretch()