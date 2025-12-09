import sys
import os

# Add the project root to the Python path to allow absolute imports from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt6.QtWidgets import QApplication, QMessageBox
from src.ui.main_window import MainWindow


def init_database():
    """
    Inicializa la conexión a MySQL.
    Retorna la instancia de la base de datos y el ID del usuario.
    """
    try:
        from src.core.mysql_database import MySQLDatabase
        
        # Configuración de MySQL (localhost por defecto)
        db = MySQLDatabase(
            host="localhost",
            user="root",
            password="",
            database="calcquest"
        )
        
        if db.connection:
            # Crear o obtener usuario de prueba
            user_id = db.get_or_create_test_user()
            print(f"✅ Base de datos MySQL inicializada. Usuario ID: {user_id}")
            return db, user_id
        else:
            print("⚠️ No se pudo conectar a MySQL. Usando modo sin base de datos.")
            return None, None
            
    except ImportError:
        print("⚠️ mysql-connector-python no instalado. Usando modo sin base de datos.")
        return None, None
    except Exception as e:
        print(f"⚠️ Error al conectar MySQL: {e}. Usando modo sin base de datos.")
        return None, None


def main():
    app = QApplication(sys.argv)
    
    # Apply global styles (QSS) - Light Mode
    app.setStyleSheet("""
        QWidget {
            background-color: #f8fafc;
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
        QPushButton:disabled {
            background-color: #cbd5e1;
            color: #94a3b8;
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
            background-color: transparent;
        }
        QScrollArea {
            border: none;
            background-color: transparent;
        }
        QScrollBar:vertical {
            background-color: #f1f5f9;
            width: 10px;
            border-radius: 5px;
        }
        QScrollBar::handle:vertical {
            background-color: #cbd5e1;
            border-radius: 5px;
            min-height: 30px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #94a3b8;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0;
        }
        QTabWidget::pane {
            background-color: white;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
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
        QProgressBar {
            background-color: #e2e8f0;
            border-radius: 5px;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: #6366f1;
            border-radius: 5px;
        }
    """)
    
    # Inicializar base de datos
    db, user_id = init_database()
    
    # Crear ventana principal con la base de datos
    window = MainWindow(db=db, user_id=user_id)
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()