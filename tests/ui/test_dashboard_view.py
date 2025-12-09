import pytest
from PyQt6.QtWidgets import QLabel, QProgressBar
from src.ui.dashboard_view import DashboardView

from src.ui.dashboard_view import DashboardView, StatCard

def test_dashboard_elements(qtbot):
    view = DashboardView()
    qtbot.addWidget(view)
    
    # Check for core gamification elements (Stat Cards)
    # Note: IDs might not be directly queryable if inside nested layouts without explicit findChild recursive or direct object name
    # But we set objectNames in dashboard_view.py
    
    streak_card = view.findChild(StatCard, "streak_card")
    xp_card = view.findChild(StatCard, "xp_card")
    level_card = view.findChild(StatCard, "level_card")
    
    assert streak_card is not None
    assert xp_card is not None
    assert level_card is not None

def test_welcome_message(qtbot):
    view = DashboardView()
    qtbot.addWidget(view)
    
    welcome = view.findChild(QLabel, "welcome_label")
    assert welcome is not None
    assert "Hola" in welcome.text()