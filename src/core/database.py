"""
Sistema de persistencia de datos para CalcQuest.
Utiliza SQLite para almacenar el progreso del usuario.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, date
from typing import Optional, Dict, List
import os


class Database:
    """
    Gestor de base de datos SQLite para CalcQuest.
    Almacena progreso del usuario, achievements, skill tree, y configuración.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Inicializa la conexión a la base de datos.
        
        Args:
            db_path: Ruta al archivo de base de datos. Si es None, usa la ubicación por defecto.
        """
        if db_path is None:
            # Usar carpeta de datos del usuario
            app_data = Path.home() / ".calcquest"
            app_data.mkdir(exist_ok=True)
            db_path = str(app_data / "calcquest.db")
        
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self._connect()
        self._initialize_schema()
    
    def _connect(self):
        """Establece conexión con la base de datos."""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row  # Permite acceso por nombre de columna
    
    def _initialize_schema(self):
        """Inicializa el esquema de la base de datos."""
        cursor = self.connection.cursor()
        
        # Tabla de progreso del usuario
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE DEFAULT 'default_user',
                total_xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                current_streak INTEGER DEFAULT 0,
                max_streak INTEGER DEFAULT 0,
                currency INTEGER DEFAULT 0,
                exercises_completed INTEGER DEFAULT 0,
                equations_solved INTEGER DEFAULT 0,
                last_activity_date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de módulos completados
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS completed_modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'default_user',
                module_id TEXT NOT NULL,
                completed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, module_id)
            )
        """)
        
        # Tabla de achievements
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'default_user',
                achievement_id TEXT NOT NULL,
                unlocked_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, achievement_id)
            )
        """)
        
        # Tabla de skill tree (nodos desbloqueados)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skill_tree (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'default_user',
                node_id TEXT NOT NULL,
                unlocked_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, node_id)
            )
        """)
        
        # Tabla de historial de actividad
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'default_user',
                activity_type TEXT NOT NULL,
                activity_data TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de configuración
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'default_user',
                key TEXT NOT NULL,
                value TEXT,
                UNIQUE(user_id, key)
            )
        """)
        
        # Crear índices para mejorar rendimiento
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_user ON activity_history(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_achievements_user ON achievements(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_skills_user ON skill_tree(user_id)")
        
        self.connection.commit()
    
    def save_user_progress(self, user_id: str, progress_data: Dict) -> bool:
        """
        Guarda el progreso del usuario.
        
        Args:
            user_id: ID del usuario
            progress_data: Diccionario con datos de progreso
            
        Returns:
            True si se guardó correctamente
        """
        cursor = self.connection.cursor()
        
        try:
            # Insertar o actualizar progreso
            cursor.execute("""
                INSERT INTO user_progress (
                    user_id, total_xp, level, current_streak, max_streak,
                    currency, exercises_completed, equations_solved,
                    last_activity_date, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    total_xp = excluded.total_xp,
                    level = excluded.level,
                    current_streak = excluded.current_streak,
                    max_streak = excluded.max_streak,
                    currency = excluded.currency,
                    exercises_completed = excluded.exercises_completed,
                    equations_solved = excluded.equations_solved,
                    last_activity_date = excluded.last_activity_date,
                    updated_at = excluded.updated_at
            """, (
                user_id,
                progress_data.get('total_xp', 0),
                progress_data.get('level', 1),
                progress_data.get('current_streak', 0),
                progress_data.get('max_streak', 0),
                progress_data.get('currency', 0),
                progress_data.get('exercises_completed', 0),
                progress_data.get('equations_solved', 0),
                progress_data.get('last_activity_date'),
                datetime.now().isoformat()
            ))
            
            # Guardar módulos completados
            for module_id in progress_data.get('completed_modules', []):
                cursor.execute("""
                    INSERT OR IGNORE INTO completed_modules (user_id, module_id)
                    VALUES (?, ?)
                """, (user_id, module_id))
            
            # Guardar achievements
            for achievement_id in progress_data.get('unlocked_achievements', []):
                cursor.execute("""
                    INSERT OR IGNORE INTO achievements (user_id, achievement_id)
                    VALUES (?, ?)
                """, (user_id, achievement_id))
            
            # Guardar skill tree
            for node_id in progress_data.get('unlocked_skills', []):
                cursor.execute("""
                    INSERT OR IGNORE INTO skill_tree (user_id, node_id)
                    VALUES (?, ?)
                """, (user_id, node_id))
            
            self.connection.commit()
            return True
            
        except Exception as e:
            self.connection.rollback()
            print(f"Error guardando progreso: {e}")
            return False
    
    def load_user_progress(self, user_id: str = 'default_user') -> Optional[Dict]:
        """
        Carga el progreso del usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Diccionario con datos de progreso o None si no existe
        """
        cursor = self.connection.cursor()
        
        # Cargar progreso básico
        cursor.execute("""
            SELECT * FROM user_progress WHERE user_id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        progress = dict(row)
        
        # Cargar módulos completados
        cursor.execute("""
            SELECT module_id FROM completed_modules WHERE user_id = ?
        """, (user_id,))
        progress['completed_modules'] = [r['module_id'] for r in cursor.fetchall()]
        
        # Cargar achievements
        cursor.execute("""
            SELECT achievement_id FROM achievements WHERE user_id = ?
        """, (user_id,))
        progress['unlocked_achievements'] = [r['achievement_id'] for r in cursor.fetchall()]
        
        # Cargar skill tree
        cursor.execute("""
            SELECT node_id FROM skill_tree WHERE user_id = ?
        """, (user_id,))
        progress['unlocked_skills'] = [r['node_id'] for r in cursor.fetchall()]
        
        return progress
    
    def log_activity(self, user_id: str, activity_type: str, data: Dict):
        """
        Registra una actividad en el historial.
        
        Args:
            user_id: ID del usuario
            activity_type: Tipo de actividad
            data: Datos adicionales de la actividad
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO activity_history (user_id, activity_type, activity_data)
            VALUES (?, ?, ?)
        """, (user_id, activity_type, json.dumps(data)))
        self.connection.commit()
    
    def get_activity_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        """
        Obtiene el historial de actividad reciente.
        
        Args:
            user_id: ID del usuario
            limit: Número máximo de registros
            
        Returns:
            Lista de actividades
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT activity_type, activity_data, created_at
            FROM activity_history
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (user_id, limit))
        
        return [{
            'type': row['activity_type'],
            'data': json.loads(row['activity_data']) if row['activity_data'] else {},
            'timestamp': row['created_at']
        } for row in cursor.fetchall()]
    
    def save_setting(self, user_id: str, key: str, value: str):
        """Guarda una configuración."""
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO settings (user_id, key, value)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, key) DO UPDATE SET value = excluded.value
        """, (user_id, key, value))
        self.connection.commit()
    
    def get_setting(self, user_id: str, key: str, default: str = None) -> Optional[str]:
        """Obtiene una configuración."""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT value FROM settings WHERE user_id = ? AND key = ?
        """, (user_id, key))
        row = cursor.fetchone()
        return row['value'] if row else default
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """
        Obtiene el leaderboard de usuarios por XP.
        
        Returns:
            Lista de usuarios ordenados por XP
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT user_id, total_xp, level, current_streak
            FROM user_progress
            ORDER BY total_xp DESC
            LIMIT ?
        """, (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_statistics(self, user_id: str) -> Dict:
        """
        Obtiene estadísticas detalladas del usuario.
        
        Returns:
            Diccionario con estadísticas
        """
        cursor = self.connection.cursor()
        
        # Contar actividades por tipo
        cursor.execute("""
            SELECT activity_type, COUNT(*) as count
            FROM activity_history
            WHERE user_id = ?
            GROUP BY activity_type
        """, (user_id,))
        
        activity_counts = {row['activity_type']: row['count'] for row in cursor.fetchall()}
        
        # Actividades de los últimos 7 días
        cursor.execute("""
            SELECT DATE(created_at) as day, COUNT(*) as count
            FROM activity_history
            WHERE user_id = ? AND created_at >= DATE('now', '-7 days')
            GROUP BY DATE(created_at)
            ORDER BY day
        """, (user_id,))
        
        weekly_activity = {row['day']: row['count'] for row in cursor.fetchall()}
        
        return {
            'activity_counts': activity_counts,
            'weekly_activity': weekly_activity
        }
    
    def reset_user_progress(self, user_id: str = 'default_user'):
        """
        Reinicia todo el progreso del usuario.
        ¡CUIDADO! Esta operación es irreversible.
        """
        cursor = self.connection.cursor()
        
        cursor.execute("DELETE FROM user_progress WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM completed_modules WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM achievements WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM skill_tree WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM activity_history WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM settings WHERE user_id = ?", (user_id,))
        
        self.connection.commit()
    
    def close(self):
        """Cierra la conexión a la base de datos."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class ProgressManager:
    """
    Gestor de alto nivel para el progreso del usuario.
    Combina UserProgress con persistencia en base de datos.
    """
    
    def __init__(self, user_id: str = 'default_user', db: Optional[Database] = None):
        self.user_id = user_id
        self.db = db or Database()
        self._load_or_create_progress()
    
    def _load_or_create_progress(self):
        """Carga el progreso existente o crea uno nuevo."""
        from src.core.gamification import UserProgress
        
        saved_data = self.db.load_user_progress(self.user_id)
        
        self.progress = UserProgress()
        
        if saved_data:
            # Restaurar datos guardados
            self.progress.total_xp = saved_data.get('total_xp', 0)
            self.progress.level = saved_data.get('level', 1)
            self.progress.current_streak = saved_data.get('current_streak', 0)
            self.progress.max_streak = saved_data.get('max_streak', 0)
            self.progress.currency = saved_data.get('currency', 0)
            self.progress.exercises_completed = saved_data.get('exercises_completed', 0)
            self.progress.equations_solved = saved_data.get('equations_solved', 0)
            self.progress.completed_modules = saved_data.get('completed_modules', [])
            
            # Restaurar achievements
            for ach_id in saved_data.get('unlocked_achievements', []):
                if ach_id in self.progress.achievement_system.achievements:
                    self.progress.achievement_system.achievements[ach_id].is_unlocked = True
            
            # Restaurar skill tree
            for node_id in saved_data.get('unlocked_skills', []):
                if node_id in self.progress.skill_tree.nodes:
                    self.progress.skill_tree.nodes[node_id].is_unlocked = True
            
            # Restaurar fecha de última actividad
            if saved_data.get('last_activity_date'):
                try:
                    self.progress.last_activity_date = date.fromisoformat(
                        saved_data['last_activity_date']
                    )
                except:
                    pass
    
    def save(self):
        """Guarda el progreso actual."""
        self.db.save_user_progress(self.user_id, self.progress.to_dict())
    
    def add_xp(self, amount: int, source: str = "general"):
        """Añade XP y guarda automáticamente."""
        achievements = self.progress.add_xp(amount, source)
        self.save()
        return achievements
    
    def complete_exercise(self, exercise_id: str):
        """Completa un ejercicio."""
        achievements = self.progress.complete_exercise(exercise_id)
        self.save()
        return achievements
    
    def solve_equation(self, equation: str):
        """Registra una ecuación resuelta."""
        achievements = self.progress.solve_equation(equation)
        self.save()
        return achievements
    
    def update_streak(self):
        """Actualiza la racha."""
        achievements = self.progress.update_streak()
        self.save()
        return achievements
    
    def get_progress(self):
        """Obtiene el objeto UserProgress."""
        return self.progress
    
    def get_stats(self):
        """Obtiene estadísticas resumidas."""
        return self.progress.get_stats_summary()
