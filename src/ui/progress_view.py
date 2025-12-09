"""
Vista de progreso del usuario.
Muestra estadísticas, logros, niveles y gráficos de progreso.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QScrollArea, QGridLayout, QProgressBar, QTabWidget, QSizePolicy,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush
import math
from datetime import datetime, timedelta


class CircularProgress(QWidget):
    """Widget de progreso circular."""
    
    def __init__(self, value: int = 0, maximum: int = 100, 
                 color: str = "#6366f1", size: int = 120, parent=None):
        super().__init__(parent)
        self.value = value
        self.maximum = maximum
        self.color = color
        self._size = size
        
        self.setFixedSize(size, size)
    
    def setValue(self, value: int):
        self.value = min(value, self.maximum)
        self.update()
    
    def setMaximum(self, maximum: int):
        self.maximum = maximum
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Centro y radio
        center = self._size // 2
        radius = center - 10
        
        # Fondo gris
        pen = QPen(QColor("#e2e8f0"), 8)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawArc(10, 10, 2 * radius, 2 * radius, 0, 360 * 16)
        
        # Progreso
        if self.maximum > 0:
            percentage = self.value / self.maximum
            pen.setColor(QColor(self.color))
            painter.setPen(pen)
            
            # Dibujar arco desde arriba, en sentido antihorario
            start_angle = 90 * 16  # Comenzar arriba
            span_angle = int(-360 * 16 * percentage)
            painter.drawArc(10, 10, 2 * radius, 2 * radius, start_angle, span_angle)
        
        # Texto central
        painter.setPen(QPen(QColor("#1e293b")))
        font = painter.font()
        font.setPointSize(18)
        font.setBold(True)
        painter.setFont(font)
        
        text = f"{int(percentage * 100)}%" if self.maximum > 0 else "0%"
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, text)


class StatCard(QFrame):
    """Tarjeta de estadística."""
    
    def __init__(self, icono: str, titulo: str, valor: str, 
                 color: str = "#6366f1", parent=None):
        super().__init__(parent)
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
                border-left: 4px solid {color};
            }}
        """)
        
        # Sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(8)
        
        # Icono y título
        header = QHBoxLayout()
        
        icon_label = QLabel(icono)
        icon_label.setStyleSheet("font-size: 24px;")
        header.addWidget(icon_label)
        
        title_label = QLabel(titulo)
        title_label.setStyleSheet("font-size: 13px; color: #64748b;")
        header.addWidget(title_label)
        
        header.addStretch()
        layout.addLayout(header)
        
        # Valor
        self.value_label = QLabel(valor)
        self.value_label.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {color};")
        layout.addWidget(self.value_label)
        
        self.setMinimumWidth(180)
        self.setMaximumHeight(120)
    
    def update_value(self, valor: str):
        self.value_label.setText(valor)


class AchievementCard(QFrame):
    """Tarjeta de logro."""
    
    def __init__(self, achievement: dict, parent=None):
        super().__init__(parent)
        
        is_unlocked = achievement.get('desbloqueado', False)
        
        if is_unlocked:
            bg_color = "white"
            border_color = "#fcd34d"
            opacity = "1"
        else:
            bg_color = "#f8fafc"
            border_color = "#e2e8f0"
            opacity = "0.5"
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 2px solid {border_color};
                border-radius: 12px;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(12)
        
        # Icono
        icon = QLabel(achievement.get('icono', '🏆'))
        icon.setStyleSheet(f"""
            font-size: 32px;
            opacity: {opacity};
        """)
        layout.addWidget(icon)
        
        # Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        name = QLabel(achievement.get('nombre', 'Logro'))
        color = "#1e293b" if is_unlocked else "#94a3b8"
        name.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {color};")
        info_layout.addWidget(name)
        
        desc = QLabel(achievement.get('descripcion', ''))
        desc.setStyleSheet(f"font-size: 12px; color: {'#64748b' if is_unlocked else '#94a3b8'};")
        desc.setWordWrap(True)
        info_layout.addWidget(desc)
        
        if is_unlocked and achievement.get('fecha_desbloqueo'):
            date = QLabel(f"🎉 Desbloqueado: {achievement['fecha_desbloqueo']}")
            date.setStyleSheet("font-size: 11px; color: #f59e0b;")
            info_layout.addWidget(date)
        
        layout.addLayout(info_layout, stretch=1)
        
        # XP
        xp = achievement.get('xp_reward', 0)
        if xp > 0:
            xp_label = QLabel(f"+{xp} XP")
            xp_label.setStyleSheet("""
                font-size: 12px;
                font-weight: bold;
                color: #f59e0b;
                background-color: #fef3c7;
                padding: 4px 8px;
                border-radius: 10px;
            """)
            layout.addWidget(xp_label)
        
        self.setMinimumHeight(80)


class LevelProgressWidget(QFrame):
    """Widget de progreso de nivel."""
    
    def __init__(self, user_data: dict, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6366f1, stop:1 #8b5cf6);
                border-radius: 20px;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(25)
        
        # Avatar / Nivel
        nivel = user_data.get('nivel', 1)
        
        level_frame = QFrame()
        level_frame.setStyleSheet("""
            background-color: rgba(255,255,255,0.2);
            border-radius: 40px;
        """)
        level_frame.setFixedSize(80, 80)
        
        level_layout = QVBoxLayout(level_frame)
        level_layout.setContentsMargins(0, 0, 0, 0)
        
        level_label = QLabel(str(nivel))
        level_label.setStyleSheet("font-size: 32px; font-weight: bold; color: white;")
        level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        level_layout.addWidget(level_label)
        
        layout.addWidget(level_frame)
        
        # Info de nivel
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)
        
        # Nombre y título
        nombres_nivel = {
            1: "Novato", 2: "Aprendiz", 3: "Estudiante", 4: "Practicante",
            5: "Intermedio", 6: "Avanzado", 7: "Experto", 8: "Maestro",
            9: "Gran Maestro", 10: "Leyenda"
        }
        
        nombre_usuario = user_data.get('nombre', 'Usuario')
        titulo = nombres_nivel.get(nivel, "Novato")
        
        name_label = QLabel(nombre_usuario)
        name_label.setStyleSheet("font-size: 22px; font-weight: bold; color: white;")
        info_layout.addWidget(name_label)
        
        title_label = QLabel(f"🏅 {titulo}")
        title_label.setStyleSheet("font-size: 14px; color: rgba(255,255,255,0.9);")
        info_layout.addWidget(title_label)
        
        # Barra de progreso XP
        xp_actual = user_data.get('xp_total', 0)
        xp_siguiente = self._calculate_xp_for_level(nivel + 1)
        xp_nivel_actual = self._calculate_xp_for_level(nivel)
        xp_en_nivel = xp_actual - xp_nivel_actual
        xp_necesario = xp_siguiente - xp_nivel_actual
        
        progress_bar = QProgressBar()
        progress_bar.setRange(0, xp_necesario)
        progress_bar.setValue(xp_en_nivel)
        progress_bar.setTextVisible(False)
        progress_bar.setFixedHeight(10)
        progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(255,255,255,0.3);
                border-radius: 5px;
            }
            QProgressBar::chunk {
                background-color: #fcd34d;
                border-radius: 5px;
            }
        """)
        info_layout.addWidget(progress_bar)
        
        xp_text = QLabel(f"⭐ {xp_en_nivel}/{xp_necesario} XP para nivel {nivel + 1}")
        xp_text.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.8);")
        info_layout.addWidget(xp_text)
        
        layout.addLayout(info_layout, stretch=1)
        
        # Stats rápidas
        stats_layout = QVBoxLayout()
        stats_layout.setSpacing(6)
        
        ejercicios = user_data.get('ejercicios_completados', 0)
        racha = user_data.get('racha_dias', 0)
        
        stats = [
            (f"📝 {ejercicios}", "Ejercicios"),
            (f"🔥 {racha} días", "Racha"),
            (f"⭐ {xp_actual}", "XP Total"),
        ]
        
        for valor, label in stats:
            stat_widget = QLabel(valor)
            stat_widget.setStyleSheet("""
                font-size: 14px;
                font-weight: bold;
                color: white;
                background-color: rgba(255,255,255,0.2);
                padding: 6px 12px;
                border-radius: 15px;
            """)
            stats_layout.addWidget(stat_widget)
        
        layout.addLayout(stats_layout)
        
        self.setMinimumHeight(150)
    
    def _calculate_xp_for_level(self, level: int) -> int:
        """Calcula el XP necesario para un nivel."""
        return int(100 * (1.5 ** (level - 1)))


class WeeklyActivityWidget(QFrame):
    """Widget que muestra la actividad semanal."""
    
    def __init__(self, activity_data: list = None, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)
        
        # Título
        title = QLabel("📊 Actividad de la Semana")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1e293b;")
        layout.addWidget(title)
        
        # Gráfico de barras simple
        days_layout = QHBoxLayout()
        days_layout.setSpacing(10)
        
        if not activity_data:
            # Estado vacío por defecto
            activity_data = [0, 0, 0, 0, 0, 0, 0]
        
        dias = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        max_val = max(activity_data) if activity_data else 1
        
        for i, (dia, valor) in enumerate(zip(dias, activity_data)):
            day_widget = QWidget()
            day_layout = QVBoxLayout(day_widget)
            day_layout.setContentsMargins(0, 0, 0, 0)
            day_layout.setSpacing(5)
            
            # Valor
            val_label = QLabel(str(valor))
            val_label.setStyleSheet("font-size: 11px; color: #64748b;")
            val_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            day_layout.addWidget(val_label)
            
            # Barra
            bar_height = int(60 * (valor / max_val)) if max_val > 0 else 5
            bar = QFrame()
            bar.setStyleSheet("""
                background-color: #e0e7ff;
                border-radius: 4px;
            """)
            
            bar.setFixedHeight(max(bar_height, 5))
            bar.setFixedWidth(30)
            day_layout.addWidget(bar, alignment=Qt.AlignmentFlag.AlignCenter)
            
            # Día
            day_label = QLabel(dia)
            day_label.setStyleSheet("font-size: 11px; color: #64748b;")
            day_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            day_layout.addWidget(day_label)
            
            days_layout.addWidget(day_widget)
        
        layout.addLayout(days_layout)


class SkillTreeWidget(QFrame):
    """Widget del árbol de habilidades simplificado."""
    
    def __init__(self, skills: list = None, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 15, 20, 15)
        self.layout.setSpacing(15)
        
        # Título
        title = QLabel("🌳 Árbol de Habilidades")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1e293b;")
        self.layout.addWidget(title)
        
        self._content_holder = QVBoxLayout()
        self._content_holder.setSpacing(10)
        self.layout.addLayout(self._content_holder)
        
        self.set_skills(skills or [])

    def set_skills(self, skills: list):
        # Limpiar contenido previo
        while self._content_holder.count():
            item = self._content_holder.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not skills:
            placeholder = QLabel("Aún no hay habilidades registradas.")
            placeholder.setStyleSheet("font-size: 13px; color: #94a3b8;")
            self._content_holder.addWidget(placeholder)
            return
        
        for skill in skills:
            skill_widget = self._create_skill_item(skill)
            self._content_holder.addWidget(skill_widget)
    
    def _create_skill_item(self, skill: dict) -> QFrame:
        """Crea un item de habilidad."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 10px;
                padding: 5px;
            }
        """)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)
        
        # Icono
        icon = QLabel(skill.get('icono', '📚'))
        icon.setStyleSheet("font-size: 20px;")
        layout.addWidget(icon)
        
        # Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        name = QLabel(skill.get('nombre', 'Habilidad'))
        name.setStyleSheet("font-size: 13px; font-weight: bold; color: #1e293b;")
        info_layout.addWidget(name)
        
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(skill.get('progreso', 0))
        progress_bar.setTextVisible(False)
        progress_bar.setFixedHeight(6)
        color = skill.get('color', '#6366f1')
        progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #e2e8f0;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)
        info_layout.addWidget(progress_bar)
        
        layout.addLayout(info_layout, stretch=1)
        
        # Porcentaje
        pct = QLabel(f"{skill.get('progreso', 0)}%")
        pct.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {color};")
        layout.addWidget(pct)
        
        return frame


class ProgressView(QWidget):
    """Vista principal de progreso del usuario."""
    
    def __init__(self, db=None, user_id: int = None, parent=None):
        super().__init__(parent)
        self.db = db
        self.user_id = user_id
        self._setup_ui()
        self._load_data()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Scroll para todo el contenido
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: #f8fafc; }")
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(25, 25, 25, 25)
        content_layout.setSpacing(20)
        
        # Widget de nivel (placeholder, se actualiza con datos reales)
        self.level_widget = None
        self.level_placeholder = QWidget()
        content_layout.addWidget(self.level_placeholder)
        
        # Grid de estadísticas
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(15)
        content_layout.addLayout(self.stats_layout)
        
        # Fila con actividad semanal y árbol de habilidades
        row_layout = QHBoxLayout()
        row_layout.setSpacing(20)
        
        self.activity_widget = WeeklyActivityWidget(activity_data=[])
        row_layout.addWidget(self.activity_widget)
        
        self.skill_tree = SkillTreeWidget(skills=[])
        row_layout.addWidget(self.skill_tree)
        
        content_layout.addLayout(row_layout)
        
        # Tabs para logros y estadísticas detalladas
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                border-top-left-radius: 0;
            }
            QTabBar::tab {
                background-color: #f1f5f9;
                color: #64748b;
                padding: 10px 20px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #6366f1;
                font-weight: bold;
            }
        """)
        
        # Tab de logros
        self.achievements_tab = self._create_achievements_tab()
        tabs.addTab(self.achievements_tab, "🏆 Logros")
        
        # Tab de estadísticas detalladas
        self.detailed_stats_tab = self._create_detailed_stats_tab()
        tabs.addTab(self.detailed_stats_tab, "📊 Estadísticas")
        
        content_layout.addWidget(tabs)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
    
    def _create_achievements_tab(self) -> QWidget:
        """Crea el tab de logros."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = QHBoxLayout()
        
        title = QLabel("Tus Logros")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1e293b;")
        header.addWidget(title)
        
        header.addStretch()
        
        self.achievements_count_label = QLabel("0/0 desbloqueados")
        self.achievements_count_label.setStyleSheet("font-size: 14px; color: #64748b;")
        header.addWidget(self.achievements_count_label)
        
        layout.addLayout(header)
        
        # Grid de logros
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        self.achievements_container = QWidget()
        self.achievements_layout = QVBoxLayout(self.achievements_container)
        self.achievements_layout.setSpacing(10)
        
        scroll.setWidget(self.achievements_container)
        layout.addWidget(scroll)
        
        return widget
    
    def _create_detailed_stats_tab(self) -> QWidget:
        """Crea el tab de estadísticas detalladas."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Estadísticas por categoría
        categories_frame = QFrame()
        categories_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 12px;
            }
        """)
        cat_layout = QVBoxLayout(categories_frame)
        cat_layout.setContentsMargins(15, 15, 15, 15)
        
        cat_title = QLabel("📚 Progreso por Categoría")
        cat_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1e293b;")
        cat_layout.addWidget(cat_title)
        
        self.categories_stats_layout = QVBoxLayout()
        cat_layout.addLayout(self.categories_stats_layout)
        
        layout.addWidget(categories_frame)
        
        # Historial reciente
        history_frame = QFrame()
        history_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 12px;
            }
        """)
        hist_layout = QVBoxLayout(history_frame)
        hist_layout.setContentsMargins(15, 15, 15, 15)
        
        hist_title = QLabel("📜 Actividad Reciente")
        hist_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1e293b;")
        hist_layout.addWidget(hist_title)
        
        self.history_layout = QVBoxLayout()
        hist_layout.addLayout(self.history_layout)
        
        layout.addWidget(history_frame)
        
        layout.addStretch()
        
        return widget
    
    def _load_data(self):
        """Carga los datos del usuario."""
        if self.db and self.user_id:
            try:
                user_data = self.db.get_user_progress(self.user_id)
                achievements = self.db.get_achievements(self.user_id)
                self._display_data(user_data, achievements)
                return
            except Exception as e:
                print(f"Error cargando datos: {e}")
        
        # Datos mock
        self._load_mock_data()
    
    def _load_mock_data(self):
        """Carga datos de ejemplo."""
        mock_user = {
            'nombre': 'Nuevo usuario',
            'nivel': 1,
            'xp_total': 0,
            'ejercicios_completados': 0,
            'racha_dias': 0,
            'precision_promedio': 0
        }
        
        mock_achievements = []
        
        self._display_data(mock_user, mock_achievements)
    
    def _display_data(self, user_data: dict, achievements: list):
        """Muestra los datos del usuario."""
        # Actualizar widget de nivel sin depender del placeholder borrado
        new_level_widget = LevelProgressWidget(user_data)
        target_layout = None
        insert_index = 0
        
        if self.level_placeholder is not None:
            parent = self.level_placeholder.parent()
            if parent:
                target_layout = parent.layout()
                insert_index = target_layout.indexOf(self.level_placeholder)
                target_layout.removeWidget(self.level_placeholder)
                self.level_placeholder.deleteLater()
                self.level_placeholder = None
        elif self.level_widget is not None:
            parent = self.level_widget.parent()
            if parent:
                target_layout = parent.layout()
                insert_index = target_layout.indexOf(self.level_widget)
                target_layout.removeWidget(self.level_widget)
                self.level_widget.deleteLater()
        
        if target_layout:
            target_layout.insertWidget(insert_index, new_level_widget)
        else:
            # Fallback: agregar al layout principal para evitar crasheos
            self.layout().addWidget(new_level_widget)
        
        self.level_widget = new_level_widget

        # Actualizar habilidades con datos reales (o vacíos si no hay)
        skills = user_data.get('skills', []) if user_data else []
        if hasattr(self, 'skill_tree'):
            self.skill_tree.set_skills(skills)
        
        # Actualizar estadísticas
        while self.stats_layout.count():
            item = self.stats_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        stats = [
            ("📝", "Ejercicios", str(user_data.get('ejercicios_completados', 0)), "#6366f1"),
            ("🎯", "Precisión", f"{user_data.get('precision_promedio', 0)}%", "#22c55e"),
            ("🔥", "Racha", f"{user_data.get('racha_dias', 0)} días", "#f59e0b"),
            ("⭐", "XP Total", str(user_data.get('xp_total', 0)), "#8b5cf6"),
        ]
        
        for icono, titulo, valor, color in stats:
            card = StatCard(icono, titulo, valor, color)
            self.stats_layout.addWidget(card)
        
        self.stats_layout.addStretch()
        
        # Actualizar logros
        while self.achievements_layout.count():
            item = self.achievements_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if achievements:
            unlocked = sum(1 for a in achievements if a.get('desbloqueado', False))
            self.achievements_count_label.setText(f"{unlocked}/{len(achievements)} desbloqueados")
            
            # Ordenar: desbloqueados primero
            sorted_achievements = sorted(achievements, 
                                         key=lambda x: (not x.get('desbloqueado', False), 
                                                       x.get('nombre', '')))
            
            for achievement in sorted_achievements:
                card = AchievementCard(achievement)
                self.achievements_layout.addWidget(card)
        else:
            self.achievements_count_label.setText("0/0 desbloqueados")
            empty_label = QLabel("Aún no tienes logros. Completa ejercicios para ganar XP y desbloquearlos.")
            empty_label.setStyleSheet("font-size: 13px; color: #94a3b8;")
            self.achievements_layout.addWidget(empty_label)
        
        self.achievements_layout.addStretch()
    
    def refresh(self):
        """Recarga los datos."""
        self._load_data()
