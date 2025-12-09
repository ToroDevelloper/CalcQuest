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
    assert dashboard_btn.text() == "Dashboard"
    assert solver_btn.text() == "The Solver"

def test_navigation_switching(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    
    dashboard_btn = window.sidebar.findChild(QPushButton, "btn_dashboard")
    solver_btn = window.sidebar.findChild(QPushButton, "btn_solver")
    
    # Add dummy widgets to stack to test index switching
    # MainWindow adds Dashboard (index 0) automatically in init
    # We need to add a dummy for Solver (index 1) for this test to work without full SolverView setup
    window.content_area.addWidget(QLabel("Mock Solver"))
    
    # Initial state should act like dashboard (index 0)
    assert window.content_area.currentIndex() == 0
    
    # Click Solver
    qtbot.mouseClick(solver_btn, Qt.MouseButton.LeftButton)
    assert window.content_area.currentIndex() == 1
    
    # Click Dashboard
    qtbot.mouseClick(dashboard_btn, Qt.MouseButton.LeftButton)
    assert window.content_area.currentIndex() == 0