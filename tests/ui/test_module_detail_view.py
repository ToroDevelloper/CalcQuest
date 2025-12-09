import pytest
from PyQt6.QtWidgets import QLabel, QPushButton, QListWidget
from PyQt6.QtCore import Qt
from src.ui.module_detail_view import ModuleDetailView

def test_module_detail_elements(qtbot):
    # Mock data for the view
    module_data = {
        "title": "Introducción a E.D.",
        "description": "Conceptos básicos y notación",
        "resources": ["Video: ¿Qué es una E.D.?", "Lectura: Clasificación"],
        "exercises": ["Ejercicio 1: Identificar Orden", "Ejercicio 2: Lineal vs No Lineal"]
    }
    
    view = ModuleDetailView(module_data)
    qtbot.addWidget(view)
    
    # Check Title
    title = view.findChild(QLabel, "module_title")
    assert title is not None
    assert title.text() == "Introducción a E.D."
    
    # Check Resources List
    resources_list = view.findChild(QListWidget, "resources_list")
    assert resources_list is not None
    assert resources_list.count() == 2
    
    # Check Exercises List
    exercises_list = view.findChild(QListWidget, "exercises_list")
    assert exercises_list is not None
    assert exercises_list.count() == 2
    
    # Check Back Button
    back_btn = view.findChild(QPushButton, "back_btn")
    assert back_btn is not None

def test_back_button_signal(qtbot):
    module_data = {"title": "Test", "description": "Desc", "resources": [], "exercises": []}
    view = ModuleDetailView(module_data)
    qtbot.addWidget(view)
    
    back_btn = view.findChild(QPushButton, "back_btn")
    
    with qtbot.waitSignal(view.back_requested) as blocker:
        qtbot.mouseClick(back_btn, Qt.MouseButton.LeftButton)
        
    assert blocker.signal_triggered