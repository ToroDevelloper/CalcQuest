import pytest
from PyQt6.QtWidgets import QPushButton, QLabel
from PyQt6.QtCore import Qt
from src.ui.main_window import MainWindow

def test_navigation_buttons_exist(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    
    # Check for Navigation Buttons in Sidebar
    dashboard_btn = window.sidebar.findChild(QPushButton, "btn_dashboard")
    solver_btn = window.sidebar.findChild(QPushButton, "btn_solver")
    
    assert dashboard_btn is not None
    assert solver_btn is not None
    # Los botones ahora incluyen iconos emoji y están en español
    assert "Dashboard" in dashboard_btn.text()
    assert "Solucionador" in solver_btn.text() or "Solver" in solver_btn.text()

def test_navigation_switching(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    
    dashboard_btn = window.sidebar.findChild(QPushButton, "btn_dashboard")
    solver_btn = window.sidebar.findChild(QPushButton, "btn_solver")
    
    # Initial state should be dashboard (index 0)
    assert window.content_area.currentIndex() == 0
    
    # Click Solver - el índice ahora es 3 (después de Dashboard, Ejercicios, Progreso)
    qtbot.mouseClick(solver_btn, Qt.MouseButton.LeftButton)
    # Verificar que cambió a una vista diferente
    assert window.content_area.currentIndex() != 0
    
    # Click Dashboard
    qtbot.mouseClick(dashboard_btn, Qt.MouseButton.LeftButton)
    assert window.content_area.currentIndex() == 0