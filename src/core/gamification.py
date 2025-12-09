from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
from datetime import datetime, date
import json


@dataclass
class Achievement:
    """
    Representa un logro/achievement desbloqueable.
    """
    id: str
    name: str
    description: str
    icon: str
    xp_reward: int
    condition_type: str  # 'xp_threshold', 'streak', 'exercises_completed', 'modules_completed'
    condition_value: int
    is_unlocked: bool = False
    unlocked_at: Optional[datetime] = None
    
    def check_condition(self, user_progress: 'UserProgress') -> bool:
        """Verifica si la condición del logro se cumple."""
        if self.condition_type == 'xp_threshold':
            return user_progress.total_xp >= self.condition_value
        elif self.condition_type == 'streak':
            return user_progress.current_streak >= self.condition_value
        elif self.condition_type == 'exercises_completed':
            return user_progress.exercises_completed >= self.condition_value
        elif self.condition_type == 'modules_completed':
            return len(user_progress.completed_modules) >= self.condition_value
        elif self.condition_type == 'equations_solved':
            return user_progress.equations_solved >= self.condition_value
        return False


@dataclass
class SkillNode:
    """
    Representa un nodo en el árbol de habilidades.
    """
    id: str
    name: str
    description: str
    icon: str
    parent_id: Optional[str]  # None si es nodo raíz
    is_unlocked: bool = False
    xp_cost: int = 0
    
    # Contenido asociado al nodo
    module_id: Optional[str] = None
    exercises: List[str] = field(default_factory=list)


class SkillTree:
    """
    Árbol de habilidades para el progreso del aprendizaje.
    Define la estructura de desbloqueo progresivo de temas.
    """
    
    def __init__(self):
        self.nodes: Dict[str, SkillNode] = {}
        self._initialize_default_tree()
    
    def _initialize_default_tree(self):
        """Inicializa el árbol de habilidades por defecto."""
        # Nivel 0: Raíz
        self.add_node(SkillNode(
            id="intro",
            name="Introducción a EDOs",
            description="Conceptos básicos de ecuaciones diferenciales",
            icon="📚",
            parent_id=None,
            is_unlocked=True,  # Siempre desbloqueado
            xp_cost=0,
            module_id="intro_module"
        ))
        
        # Nivel 1: Métodos básicos
        self.add_node(SkillNode(
            id="separable",
            name="Variables Separables",
            description="Ecuaciones de la forma dy/dx = f(x)g(y)",
            icon="🔀",
            parent_id="intro",
            is_unlocked=False,
            xp_cost=50,
            module_id="separable_module"
        ))
        
        self.add_node(SkillNode(
            id="linear_first",
            name="Lineales de Primer Orden",
            description="Ecuaciones de la forma y' + P(x)y = Q(x)",
            icon="📈",
            parent_id="intro",
            is_unlocked=False,
            xp_cost=50,
            module_id="linear_first_module"
        ))
        
        # Nivel 2: Métodos intermedios
        self.add_node(SkillNode(
            id="exact",
            name="Ecuaciones Exactas",
            description="Ecuaciones de la forma M(x,y)dx + N(x,y)dy = 0",
            icon="⚖️",
            parent_id="linear_first",
            is_unlocked=False,
            xp_cost=100,
            module_id="exact_module"
        ))
        
        self.add_node(SkillNode(
            id="homogeneous",
            name="Ecuaciones Homogéneas",
            description="Ecuaciones donde f(tx,ty) = t^n f(x,y)",
            icon="🔄",
            parent_id="separable",
            is_unlocked=False,
            xp_cost=100,
            module_id="homogeneous_module"
        ))
        
        # Nivel 3: Segundo orden
        self.add_node(SkillNode(
            id="second_order_homo",
            name="Segundo Orden Homogéneas",
            description="ay'' + by' + cy = 0",
            icon="📊",
            parent_id="exact",
            is_unlocked=False,
            xp_cost=150,
            module_id="second_order_homo_module"
        ))
        
        self.add_node(SkillNode(
            id="second_order_nonhomo",
            name="Segundo Orden No Homogéneas",
            description="ay'' + by' + cy = g(x)",
            icon="🎯",
            parent_id="second_order_homo",
            is_unlocked=False,
            xp_cost=200,
            module_id="second_order_nonhomo_module"
        ))
        
        # Nivel 4: Avanzado
        self.add_node(SkillNode(
            id="laplace",
            name="Transformada de Laplace",
            description="Método de transformadas para resolver EDOs",
            icon="🌊",
            parent_id="second_order_nonhomo",
            is_unlocked=False,
            xp_cost=250,
            module_id="laplace_module"
        ))
        
        self.add_node(SkillNode(
            id="systems",
            name="Sistemas de EDOs",
            description="Sistemas de ecuaciones diferenciales",
            icon="🔗",
            parent_id="second_order_nonhomo",
            is_unlocked=False,
            xp_cost=300,
            module_id="systems_module"
        ))
    
    def add_node(self, node: SkillNode):
        """Añade un nodo al árbol."""
        self.nodes[node.id] = node
    
    def get_node(self, node_id: str) -> Optional[SkillNode]:
        """Obtiene un nodo por su ID."""
        return self.nodes.get(node_id)
    
    def can_unlock(self, node_id: str, user_progress: 'UserProgress') -> bool:
        """Verifica si un nodo puede ser desbloqueado."""
        node = self.get_node(node_id)
        if not node:
            return False
        
        # Ya está desbloqueado
        if node.is_unlocked:
            return False
        
        # Verificar que el padre esté desbloqueado
        if node.parent_id:
            parent = self.get_node(node.parent_id)
            if not parent or not parent.is_unlocked:
                return False
        
        # Verificar XP suficiente
        return user_progress.total_xp >= node.xp_cost
    
    def unlock_node(self, node_id: str, user_progress: 'UserProgress') -> bool:
        """Intenta desbloquear un nodo."""
        if not self.can_unlock(node_id, user_progress):
            return False
        
        node = self.get_node(node_id)
        if node:
            node.is_unlocked = True
            return True
        return False
    
    def get_unlocked_nodes(self) -> List[SkillNode]:
        """Obtiene todos los nodos desbloqueados."""
        return [node for node in self.nodes.values() if node.is_unlocked]
    
    def get_available_nodes(self, user_progress: 'UserProgress') -> List[SkillNode]:
        """Obtiene los nodos que pueden ser desbloqueados."""
        return [node for node in self.nodes.values() 
                if self.can_unlock(node.id, user_progress)]
    
    def get_children(self, node_id: str) -> List[SkillNode]:
        """Obtiene los nodos hijos de un nodo."""
        return [node for node in self.nodes.values() if node.parent_id == node_id]
    
    def get_progress_percentage(self) -> float:
        """Calcula el porcentaje de progreso en el árbol."""
        total = len(self.nodes)
        unlocked = len(self.get_unlocked_nodes())
        return (unlocked / total * 100) if total > 0 else 0


class AchievementSystem:
    """
    Sistema de logros/achievements del juego.
    """
    
    def __init__(self):
        self.achievements: Dict[str, Achievement] = {}
        self._initialize_default_achievements()
    
    def _initialize_default_achievements(self):
        """Inicializa los logros por defecto."""
        default_achievements = [
            Achievement(
                id="first_step",
                name="Primeros Pasos",
                description="Completa tu primer ejercicio",
                icon="🎯",
                xp_reward=25,
                condition_type="exercises_completed",
                condition_value=1
            ),
            Achievement(
                id="streak_3",
                name="En Racha",
                description="Mantén una racha de 3 días",
                icon="🔥",
                xp_reward=50,
                condition_type="streak",
                condition_value=3
            ),
            Achievement(
                id="streak_7",
                name="Semana Perfecta",
                description="Mantén una racha de 7 días",
                icon="⭐",
                xp_reward=100,
                condition_type="streak",
                condition_value=7
            ),
            Achievement(
                id="streak_30",
                name="Mes de Dedicación",
                description="Mantén una racha de 30 días",
                icon="🏆",
                xp_reward=500,
                condition_type="streak",
                condition_value=30
            ),
            Achievement(
                id="xp_100",
                name="Aprendiz",
                description="Alcanza 100 XP",
                icon="📗",
                xp_reward=25,
                condition_type="xp_threshold",
                condition_value=100
            ),
            Achievement(
                id="xp_500",
                name="Estudiante Dedicado",
                description="Alcanza 500 XP",
                icon="📘",
                xp_reward=50,
                condition_type="xp_threshold",
                condition_value=500
            ),
            Achievement(
                id="xp_1000",
                name="Matemático en Formación",
                description="Alcanza 1000 XP",
                icon="📕",
                xp_reward=100,
                condition_type="xp_threshold",
                condition_value=1000
            ),
            Achievement(
                id="solver_10",
                name="Calculadora Humana",
                description="Resuelve 10 ecuaciones",
                icon="🧮",
                xp_reward=75,
                condition_type="equations_solved",
                condition_value=10
            ),
            Achievement(
                id="solver_50",
                name="Maestro del Cálculo",
                description="Resuelve 50 ecuaciones",
                icon="🎓",
                xp_reward=200,
                condition_type="equations_solved",
                condition_value=50
            ),
            Achievement(
                id="exercises_10",
                name="Practicante",
                description="Completa 10 ejercicios",
                icon="✏️",
                xp_reward=50,
                condition_type="exercises_completed",
                condition_value=10
            ),
            Achievement(
                id="exercises_50",
                name="Ejercitador Pro",
                description="Completa 50 ejercicios",
                icon="💪",
                xp_reward=150,
                condition_type="exercises_completed",
                condition_value=50
            ),
            Achievement(
                id="module_1",
                name="Primer Módulo",
                description="Completa tu primer módulo",
                icon="📦",
                xp_reward=100,
                condition_type="modules_completed",
                condition_value=1
            ),
            Achievement(
                id="module_5",
                name="Explorador",
                description="Completa 5 módulos",
                icon="🗺️",
                xp_reward=300,
                condition_type="modules_completed",
                condition_value=5
            ),
        ]
        
        for achievement in default_achievements:
            self.achievements[achievement.id] = achievement
    
    def check_and_unlock(self, user_progress: 'UserProgress') -> List[Achievement]:
        """
        Verifica y desbloquea los logros que correspondan.
        Retorna la lista de logros recién desbloqueados.
        """
        newly_unlocked = []
        
        for achievement in self.achievements.values():
            if not achievement.is_unlocked:
                if achievement.check_condition(user_progress):
                    achievement.is_unlocked = True
                    achievement.unlocked_at = datetime.now()
                    newly_unlocked.append(achievement)
        
        return newly_unlocked
    
    def get_unlocked(self) -> List[Achievement]:
        """Obtiene todos los logros desbloqueados."""
        return [a for a in self.achievements.values() if a.is_unlocked]
    
    def get_locked(self) -> List[Achievement]:
        """Obtiene todos los logros pendientes."""
        return [a for a in self.achievements.values() if not a.is_unlocked]
    
    def get_progress_percentage(self) -> float:
        """Calcula el porcentaje de logros desbloqueados."""
        total = len(self.achievements)
        unlocked = len(self.get_unlocked())
        return (unlocked / total * 100) if total > 0 else 0


class UserProgress:
    """
    Gestiona el progreso del usuario incluyendo XP, rachas, logros y skill tree.
    """
    
    def __init__(self):
        # Estadísticas básicas
        self.xp = 0  # Alias para compatibilidad
        self.total_xp = 0
        self.current_streak = 0
        self.max_streak = 0
        self.currency = 0
        self.level = 1
        self._xp_per_level = 100
        
        # Tracking de actividad
        self.last_activity_date: Optional[date] = None
        self.exercises_completed = 0
        self.equations_solved = 0
        self.completed_modules: List[str] = []
        
        # Sistemas de gamificación
        self.skill_tree = SkillTree()
        self.achievement_system = AchievementSystem()
        
        # Historial
        self.activity_history: List[Dict] = []
    
    @property
    def xp(self):
        return self.total_xp
    
    @xp.setter
    def xp(self, value):
        self.total_xp = value

    def add_xp(self, amount: int, source: str = "general") -> List[Achievement]:
        """
        Añade XP al usuario y verifica logros.
        Retorna la lista de logros desbloqueados.
        """
        self.total_xp += amount
        self._check_level_up()
        
        # Registrar actividad
        self._log_activity("xp_gained", {"amount": amount, "source": source})
        
        # Verificar logros
        return self.achievement_system.check_and_unlock(self)

    def _check_level_up(self):
        """Verifica y actualiza el nivel del usuario."""
        old_level = self.level
        self.level = 1 + (self.total_xp // self._xp_per_level)
        
        if self.level > old_level:
            self._log_activity("level_up", {"new_level": self.level})
    
    def get_xp_for_next_level(self) -> int:
        """Obtiene el XP necesario para el siguiente nivel."""
        return self.level * self._xp_per_level
    
    def get_xp_progress_in_level(self) -> float:
        """Obtiene el progreso de XP dentro del nivel actual (0-100%)."""
        xp_for_current = (self.level - 1) * self._xp_per_level
        xp_in_level = self.total_xp - xp_for_current
        xp_needed = self._xp_per_level
        return (xp_in_level / xp_needed * 100) if xp_needed > 0 else 100

    def update_streak(self) -> List[Achievement]:
        """
        Actualiza la racha del usuario basándose en la fecha actual.
        Debe llamarse una vez al día cuando el usuario hace actividad.
        """
        today = date.today()
        
        if self.last_activity_date is None:
            # Primera actividad
            self.current_streak = 1
        elif self.last_activity_date == today:
            # Ya registrado hoy, no hacer nada
            pass
        elif (today - self.last_activity_date).days == 1:
            # Día consecutivo
            self.current_streak += 1
        else:
            # Racha rota
            self.current_streak = 1
        
        # Actualizar máximo
        if self.current_streak > self.max_streak:
            self.max_streak = self.current_streak
        
        self.last_activity_date = today
        self._log_activity("streak_updated", {"streak": self.current_streak})
        
        return self.achievement_system.check_and_unlock(self)

    def increment_streak(self):
        """Método legacy para compatibilidad con tests."""
        self.current_streak += 1
        if self.current_streak > self.max_streak:
            self.max_streak = self.current_streak

    def reset_streak(self):
        """Reinicia la racha actual."""
        self.current_streak = 0

    def add_currency(self, amount: int):
        """Añade moneda virtual."""
        self.currency += amount
        self._log_activity("currency_gained", {"amount": amount})

    def spend_currency(self, amount: int) -> bool:
        """Gasta moneda virtual. Retorna True si exitoso."""
        if amount > self.currency:
            raise ValueError("Not enough currency")
        self.currency -= amount
        self._log_activity("currency_spent", {"amount": amount})
        return True
    
    def complete_exercise(self, exercise_id: str, xp_earned: int = 25) -> List[Achievement]:
        """Registra un ejercicio completado."""
        self.exercises_completed += 1
        self._log_activity("exercise_completed", {"id": exercise_id})
        return self.add_xp(xp_earned, source="exercise")
    
    def solve_equation(self, equation: str, xp_earned: int = 15) -> List[Achievement]:
        """Registra una ecuación resuelta."""
        self.equations_solved += 1
        self._log_activity("equation_solved", {"equation": equation})
        return self.add_xp(xp_earned, source="solver")
    
    def complete_module(self, module_id: str, xp_earned: int = 100) -> List[Achievement]:
        """Registra un módulo completado."""
        if module_id not in self.completed_modules:
            self.completed_modules.append(module_id)
            self._log_activity("module_completed", {"id": module_id})
            return self.add_xp(xp_earned, source="module")
        return []
    
    def unlock_skill(self, node_id: str) -> bool:
        """Intenta desbloquear un nodo del skill tree."""
        return self.skill_tree.unlock_node(node_id, self)
    
    def _log_activity(self, activity_type: str, data: Dict):
        """Registra una actividad en el historial."""
        self.activity_history.append({
            "type": activity_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
    
    def to_dict(self) -> Dict:
        """Convierte el progreso a diccionario para serialización."""
        return {
            "total_xp": self.total_xp,
            "level": self.level,
            "current_streak": self.current_streak,
            "max_streak": self.max_streak,
            "currency": self.currency,
            "exercises_completed": self.exercises_completed,
            "equations_solved": self.equations_solved,
            "completed_modules": self.completed_modules,
            "last_activity_date": self.last_activity_date.isoformat() if self.last_activity_date else None,
            "unlocked_skills": [n.id for n in self.skill_tree.get_unlocked_nodes()],
            "unlocked_achievements": [a.id for a in self.achievement_system.get_unlocked()]
        }
    
    def get_stats_summary(self) -> Dict:
        """Obtiene un resumen de estadísticas para mostrar en UI."""
        return {
            "level": self.level,
            "total_xp": self.total_xp,
            "xp_progress": self.get_xp_progress_in_level(),
            "xp_to_next": self.get_xp_for_next_level(),
            "streak": self.current_streak,
            "max_streak": self.max_streak,
            "currency": self.currency,
            "exercises": self.exercises_completed,
            "equations": self.equations_solved,
            "modules": len(self.completed_modules),
            "skills_unlocked": len(self.skill_tree.get_unlocked_nodes()),
            "skills_total": len(self.skill_tree.nodes),
            "achievements_unlocked": len(self.achievement_system.get_unlocked()),
            "achievements_total": len(self.achievement_system.achievements)
        }