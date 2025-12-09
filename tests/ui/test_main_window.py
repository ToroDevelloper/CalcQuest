import pytest
from PyQt6.QtCore import Qt
from src.ui.main_window import MainWindow

def test_window_title(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    
    assert window.windowTitle() == "CalcQuest - Tu Aventura Matemática"

def test_initial_layout(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    
    # Check if we have the main navigation components described in the TDD
    # Sidebar or BottomBar, and a stacked widget for views
    
    # Assuming Sidebar for Desktop focus as per "2.2 Estructura de Módulos"
    # and "5. Estrategia de Interfaz" -> "Barra lateral icónica simple"
    
    assert window.findChild(object, "sidebar") is not None
    assert window.findChild(object, "content_area") is not None