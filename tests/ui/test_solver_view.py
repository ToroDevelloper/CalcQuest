import pytest
from PyQt6.QtWidgets import QLineEdit, QPushButton, QListWidget
from PyQt6.QtCore import Qt
from src.ui.solver_view import SolverView

def test_solver_interface_elements(qtbot):
    view = SolverView()
    qtbot.addWidget(view)
    
    # Check for Chat History area
    assert view.findChild(QListWidget, "chat_history") is not None
    
    # Check for Input field
    input_field = view.findChild(QLineEdit, "input_field")
    assert input_field is not None
    
    # Check for Send button
    send_btn = view.findChild(QPushButton, "send_btn")
    assert send_btn is not None

def test_send_message_flow(qtbot):
    view = SolverView()
    qtbot.addWidget(view)
    
    input_field = view.findChild(QLineEdit, "input_field")
    send_btn = view.findChild(QPushButton, "send_btn")
    chat_history = view.findChild(QListWidget, "chat_history")
    
    # Type message
    qtbot.keyClicks(input_field, "y' + 2y = e^x")
    
    # Click send
    qtbot.mouseClick(send_btn, Qt.MouseButton.LeftButton)
    
    # Check if message appeared in history (User)
    # Note: The solver now adds multiple messages (Introduction + Steps)
    # We need to find the user message in the list
    
    found_user_msg = False
    for i in range(chat_history.count()):
        item = chat_history.item(i)
        if "Tú: y' + 2y = e^x" in item.text():
            found_user_msg = True
            break
            
    assert found_user_msg
    
    # Check if input cleared
    assert input_field.text() == ""