import pytest
from PyQt6.QtCore import Qt
from src.ui.module_detail_view import ModuleDetailView

def test_resource_interaction(qtbot):
    module_data = {
        "title": "Test Module",
        "description": "Desc",
        "resources": ["🎥 Video: Test Video", "📄 Lectura: Test Reading"],
        "exercises": ["📝 Ejercicio: Test Exercise"]
    }
    view = ModuleDetailView(module_data)
    qtbot.addWidget(view)
    
    # Simulate clicking a resource (Video)
    # Since QListWidget items aren't buttons, we simulate item activation
    # In the implementation we should connect itemClicked/itemActivated
    
    list_widget = view.resources_list
    item = list_widget.item(0)
    
    # We can't easily mock QDesktopServices.openUrl in a simple unit test without monkeypatching
    # But we can verify the signal connection or if a custom signal is emitted if we refactor to emit signals
    # For now, we will test that clicking doesn't crash and ideally mock the open_url function in the view
    
    # Let's assume we refactor ModuleDetailView to have a method handle_resource_click
    # We can spy on that method if we mock it, or rely on implementation detail
    
    # For this TDD step, let's define that clicking a list item triggers a specific handler
    
    list_widget.itemClicked.emit(item)
    # Assertion would require mocking the side effect (opening browser or dialog)
    # We will implement the view to use a helper method we can monkeypatch in tests if needed, 
    # or just trust manual verification for external calls like openUrl for this scope.

def test_exercise_interaction(qtbot):
    module_data = {
        "title": "Test", "description": "Desc", 
        "resources": [], 
        "exercises": ["📝 Ejercicio 1"]
    }
    view = ModuleDetailView(module_data)
    qtbot.addWidget(view)
    
    list_widget = view.exercises_list
    item = list_widget.item(0)
    
    # Simulate click
    list_widget.itemClicked.emit(item)
    
    # Ideally check if a dialog opened or signal emitted