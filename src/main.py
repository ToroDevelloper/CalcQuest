import sys
import os

# Add the project root to the Python path to allow absolute imports from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.ui.solver_view import SolverView
from src.ui.visualizer_view import VisualizerView
from src.ui.module_detail_view import ModuleDetailView

def main():
    app = QApplication(sys.argv)
    
    # Apply global styles (QSS) - Light Mode
    app.setStyleSheet("""
        QWidget {
            background-color: #f0f4f8;
            color: #1e293b;
            font-family: 'Segoe UI', sans-serif;
            font-size: 14px;
        }
        QPushButton {
            background-color: #6366f1;
            color: white;
            border-radius: 8px;
            padding: 10px 20px;
            margin: 5px;
            font-weight: bold;
            border: none;
        }
        QPushButton:hover {
            background-color: #4f46e5;
        }
        QLineEdit {
            background-color: white;
            color: #1e293b;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 12px;
        }
        QLineEdit:focus {
            border: 2px solid #6366f1;
        }
        QListWidget {
            background-color: white;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 10px;
            color: #1e293b;
        }
        QLabel {
            color: #1e293b;
        }
        /* Sidebar specific styles */
        QWidget#sidebar {
            background-color: white;
            border-right: 1px solid #e2e8f0;
        }
        QWidget#sidebar QPushButton {
            text-align: left;
            background-color: transparent;
            color: #64748b;
            border: none;
            margin: 5px 15px;
            padding: 10px;
        }
        QWidget#sidebar QPushButton:hover {
            background-color: #f1f5f9;
            color: #6366f1;
            border-radius: 10px;
        }
    """)
    
    window = MainWindow()
    
    # Inject Solver View into Main Window (Composition Root)
    # Note: MainWindow now handles its own basic setup, but we inject specific views
    # Ideally, we would have a ViewFactory, but for this scale direct injection works
    solver_view = SolverView()
    
    # Add views to stack (Dashboard is 0, Solver is 1)
    # Note: We need to replace the placeholder dashboard with the real one
    # Ideally MainWindow should accept views, but for now we manipulate the stack
    
    # Remove initial placeholder
    initial_widget = window.content_area.widget(0)
    window.content_area.removeWidget(initial_widget)
    initial_widget.deleteLater()
    
    # Add Real Dashboard
    from src.ui.dashboard_view import DashboardView
    dashboard_view = DashboardView()
    window.content_area.addWidget(dashboard_view) # Index 0
    
    # Add Solver
    window.content_area.addWidget(solver_view) # Index 1
    
    # Add Visualizer
    visualizer_view = VisualizerView()
    window.content_area.addWidget(visualizer_view) # Index 2
    
    # Add Module Detail View (Introduction)
    intro_data = {
        "title": "Introducción a Ecuaciones Diferenciales",
        "description": "Una ecuación diferencial es una ecuación matemática que relaciona una función con sus derivadas. En las aplicaciones, las funciones usualmente representan cantidades físicas, las derivadas representan sus razones de cambio y la ecuación define la relación entre ellas.",
        "resources": [
            "🎥 Video: ¿Qué son las E.D.?",
            "📄 Lectura: Clasificación por Orden y Linealidad",
            "📄 Lectura: Interpretación Geométrica"
        ],
        "exercises": [
            "📝 Ejercicio 1: Identificar Variable Dependiente e Independiente",
            "📝 Ejercicio 2: Determinar el Orden de la Ecuación",
            "📝 Ejercicio 3: Verificar si es Lineal o No Lineal"
        ]
    }
    intro_view = ModuleDetailView(intro_data)
    window.content_area.addWidget(intro_view) # Index 3
    
    # Connect Dashboard Signals (Navigation from Cards)
    
    # "Variables Separables" -> Solver
    dashboard_view.request_solver.connect(lambda: window.content_area.setCurrentIndex(1))
    
    # "Introducción" -> Module Detail
    dashboard_view.request_intro.connect(lambda: window.content_area.setCurrentIndex(3))
    
    # Connect Back Buttons
    intro_view.back_requested.connect(lambda: window.content_area.setCurrentIndex(0))

    # Ensure Dashboard is first shown
    window.content_area.setCurrentIndex(0)
    
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()