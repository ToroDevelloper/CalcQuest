"""
Sistema de persistencia de datos con MySQL para CalcQuest.
Gestiona usuarios, progreso, ejercicios y niveles.
"""

import mysql.connector
from mysql.connector import Error
from typing import Optional, Dict, List, Tuple
from datetime import datetime, date
import json
import hashlib


class MySQLDatabase:
    """
    Gestor de base de datos MySQL para CalcQuest.
    Almacena progreso del usuario, ejercicios por niveles, y estadísticas.
    """
    
    def __init__(self, host: str = "localhost", user: str = "root", 
                 password: str = "", database: str = "calcquest"):
        """
        Inicializa la conexión a MySQL.
        
        Args:
            host: Host del servidor MySQL (default: localhost)
            user: Usuario de MySQL (default: root)
            password: Contraseña de MySQL (default: vacío)
            database: Nombre de la base de datos
        """
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database
        }
        self.connection = None
        self._connect()
        self._initialize_database()
    
    def _connect(self):
        """Establece conexión con MySQL."""
        try:
            # Primero conectar sin base de datos para crearla si no existe
            temp_config = {k: v for k, v in self.config.items() if k != 'database'}
            temp_conn = mysql.connector.connect(**temp_config)
            cursor = temp_conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            temp_conn.close()
            
            # Ahora conectar a la base de datos
            self.connection = mysql.connector.connect(**self.config)
            print(f"✅ Conectado a MySQL: {self.config['database']}")
        except Error as e:
            print(f"❌ Error conectando a MySQL: {e}")
            self.connection = None
    
    def _initialize_database(self):
        """Crea las tablas necesarias."""
        if not self.connection:
            return
        
        cursor = self.connection.cursor()
        
        # Tabla de usuarios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                nombre VARCHAR(100),
                avatar VARCHAR(50) DEFAULT '🧑‍🎓',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP NULL
            ) ENGINE=InnoDB
        """)
        
        # Tabla de progreso del usuario
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS progreso_usuario (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT NOT NULL,
                total_xp INT DEFAULT 0,
                nivel INT DEFAULT 1,
                racha_actual INT DEFAULT 0,
                racha_maxima INT DEFAULT 0,
                monedas INT DEFAULT 0,
                ejercicios_completados INT DEFAULT 0,
                ecuaciones_resueltas INT DEFAULT 0,
                ultima_actividad DATE,
                tiempo_total_minutos INT DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            ) ENGINE=InnoDB
        """)
        
        # Tabla de categorías/temas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categorias (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                descripcion TEXT,
                icono VARCHAR(10) DEFAULT '📚',
                orden INT DEFAULT 0,
                nivel_requerido INT DEFAULT 1,
                xp_recompensa INT DEFAULT 100,
                is_active BOOLEAN DEFAULT TRUE
            ) ENGINE=InnoDB
        """)
        
        # Tabla de niveles de dificultad
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS niveles_dificultad (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(50) NOT NULL,
                descripcion VARCHAR(255),
                multiplicador_xp DECIMAL(3,2) DEFAULT 1.00,
                color VARCHAR(7) DEFAULT '#6366f1',
                icono VARCHAR(10) DEFAULT '⭐'
            ) ENGINE=InnoDB
        """)
        
        # Tabla de ejercicios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ejercicios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                categoria_id INT NOT NULL,
                nivel_id INT NOT NULL,
                titulo VARCHAR(200) NOT NULL,
                problema TEXT NOT NULL,
                ecuacion_latex VARCHAR(500),
                tipo_respuesta ENUM('texto', 'opcion_multiple', 'numerico', 'ecuacion') DEFAULT 'texto',
                respuestas_correctas JSON,
                opciones JSON,
                pista TEXT,
                explicacion TEXT,
                xp_base INT DEFAULT 25,
                tiempo_limite_segundos INT DEFAULT 300,
                orden INT DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB
        """)
        
        # Tabla de progreso por ejercicio
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS progreso_ejercicios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT NOT NULL,
                ejercicio_id INT NOT NULL,
                completado BOOLEAN DEFAULT FALSE,
                intentos INT DEFAULT 0,
                mejor_tiempo_segundos INT,
                xp_ganado INT DEFAULT 0,
                primera_vez_correcto BOOLEAN DEFAULT FALSE,
                completed_at TIMESTAMP NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                FOREIGN KEY (ejercicio_id) REFERENCES ejercicios(id) ON DELETE CASCADE,
                UNIQUE KEY unique_usuario_ejercicio (usuario_id, ejercicio_id)
            ) ENGINE=InnoDB
        """)
        
        # Tabla de logros/achievements
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logros (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                descripcion VARCHAR(255),
                icono VARCHAR(10) DEFAULT '🏆',
                tipo_condicion ENUM('xp', 'racha', 'ejercicios', 'categoria', 'tiempo') NOT NULL,
                valor_condicion INT NOT NULL,
                xp_recompensa INT DEFAULT 50,
                is_secret BOOLEAN DEFAULT FALSE
            ) ENGINE=InnoDB
        """)
        
        # Tabla de logros desbloqueados
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logros_usuario (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT NOT NULL,
                logro_id INT NOT NULL,
                unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                FOREIGN KEY (logro_id) REFERENCES logros(id) ON DELETE CASCADE,
                UNIQUE KEY unique_usuario_logro (usuario_id, logro_id)
            ) ENGINE=InnoDB
        """)
        
        # Tabla de categorías desbloqueadas (skill tree)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categorias_usuario (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT NOT NULL,
                categoria_id INT NOT NULL,
                desbloqueado BOOLEAN DEFAULT FALSE,
                progreso_porcentaje DECIMAL(5,2) DEFAULT 0.00,
                unlocked_at TIMESTAMP NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE CASCADE,
                UNIQUE KEY unique_usuario_categoria (usuario_id, categoria_id)
            ) ENGINE=InnoDB
        """)
        
        # Tabla de historial de actividad
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historial_actividad (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT NOT NULL,
                tipo_actividad VARCHAR(50) NOT NULL,
                descripcion VARCHAR(255),
                xp_ganado INT DEFAULT 0,
                datos_extra JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                INDEX idx_usuario_fecha (usuario_id, created_at)
            ) ENGINE=InnoDB
        """)
        
        self.connection.commit()
        
        # Insertar datos iniciales
        self._insert_initial_data(cursor)
        self.connection.commit()
    
    def _insert_initial_data(self, cursor):
        """Inserta datos iniciales si no existen."""
        
        # Verificar si ya hay niveles
        cursor.execute("SELECT COUNT(*) FROM niveles_dificultad")
        if cursor.fetchone()[0] == 0:
            niveles = [
                ("Principiante", "Para empezar desde cero", 1.0, "#22c55e", "🌱"),
                ("Básico", "Conceptos fundamentales", 1.25, "#3b82f6", "⭐"),
                ("Intermedio", "Aplicaciones prácticas", 1.5, "#f59e0b", "🔥"),
                ("Avanzado", "Problemas complejos", 2.0, "#ef4444", "💎"),
                ("Experto", "Desafíos de maestría", 3.0, "#8b5cf6", "👑")
            ]
            cursor.executemany("""
                INSERT INTO niveles_dificultad (nombre, descripcion, multiplicador_xp, color, icono)
                VALUES (%s, %s, %s, %s, %s)
            """, niveles)
        
        # Verificar si ya hay categorías
        cursor.execute("SELECT COUNT(*) FROM categorias")
        if cursor.fetchone()[0] == 0:
            categorias = [
                # Nivel 1: Fundamentos
                ("Introducción a EDOs", "Conceptos básicos de ecuaciones diferenciales", "📚", 1, 1, 50),
                ("Derivadas Básicas", "Reglas fundamentales de derivación", "📐", 2, 1, 75),
                ("Integrales Básicas", "Técnicas básicas de integración", "∫", 3, 1, 75),
                
                # Nivel 2: EDOs de Primer Orden
                ("Variables Separables", "Ecuaciones de la forma dy/dx = f(x)g(y)", "🔀", 4, 2, 100),
                ("EDOs Lineales 1er Orden", "Factor integrante y soluciones", "📈", 5, 2, 100),
                ("Ecuaciones Exactas", "M(x,y)dx + N(x,y)dy = 0", "⚖️", 6, 3, 125),
                
                # Nivel 3: EDOs de Segundo Orden
                ("EDOs Homogéneas 2do Orden", "ay'' + by' + cy = 0", "📊", 7, 4, 150),
                ("EDOs No Homogéneas", "Variación de parámetros", "🎯", 8, 5, 175),
                
                # Nivel 4: Avanzado
                ("Transformada de Laplace", "Método de transformadas", "🌊", 9, 6, 200),
                ("Sistemas de EDOs", "Sistemas de ecuaciones", "🔗", 10, 7, 250),
                
                # Nivel 5: No Lineales
                ("EDOs No Lineales", "Ecuaciones no lineales especiales", "🌀", 11, 8, 300),
                ("Ecuaciones de Bernoulli", "Casos especiales no lineales", "🔬", 12, 8, 300),
            ]
            cursor.executemany("""
                INSERT INTO categorias (nombre, descripcion, icono, orden, nivel_requerido, xp_recompensa)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, categorias)
        
        # Verificar si ya hay ejercicios
        cursor.execute("SELECT COUNT(*) FROM ejercicios")
        if cursor.fetchone()[0] == 0:
            self._insert_exercises(cursor)
        
        # Verificar si ya hay logros
        cursor.execute("SELECT COUNT(*) FROM logros")
        if cursor.fetchone()[0] == 0:
            logros = [
                ("Primeros Pasos", "Completa tu primer ejercicio", "🎯", "ejercicios", 1, 25, False),
                ("Estudiante Dedicado", "Completa 10 ejercicios", "📖", "ejercicios", 10, 50, False),
                ("Practicante Pro", "Completa 50 ejercicios", "💪", "ejercicios", 50, 150, False),
                ("Maestro", "Completa 100 ejercicios", "🎓", "ejercicios", 100, 300, False),
                ("En Racha", "Mantén 3 días seguidos", "🔥", "racha", 3, 50, False),
                ("Semana Perfecta", "Mantén 7 días seguidos", "⭐", "racha", 7, 100, False),
                ("Mes de Dedicación", "Mantén 30 días seguidos", "🏆", "racha", 30, 500, False),
                ("Centenario", "Alcanza 100 XP", "💯", "xp", 100, 25, False),
                ("Medio Millar", "Alcanza 500 XP", "🌟", "xp", 500, 75, False),
                ("Mil Puntos", "Alcanza 1000 XP", "💎", "xp", 1000, 150, False),
                ("Velocista", "Completa ejercicio en menos de 30s", "⚡", "tiempo", 30, 50, True),
            ]
            cursor.executemany("""
                INSERT INTO logros (nombre, descripcion, icono, tipo_condicion, valor_condicion, xp_recompensa, is_secret)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, logros)
    
    def _insert_exercises(self, cursor):
        """Inserta ejercicios iniciales organizados por categoría y nivel."""
        
        ejercicios = [
            # =====================================================
            # CATEGORÍA 1: Introducción a EDOs (Principiante)
            # =====================================================
            (1, 1, "Identificar Variables", 
             "En la ecuación dy/dx + 2y = e^x, identifica la variable dependiente e independiente.",
             r"\frac{dy}{dx} + 2y = e^x",
             "texto", 
             json.dumps(["y, x", "y,x", "dependiente: y, independiente: x", "y e x"]),
             None,
             "La variable dependiente es la que buscamos (función), la independiente es respecto a la cual derivamos.",
             "Variable dependiente: y (la función a encontrar)\nVariable independiente: x (respecto a la cual derivamos)",
             20, 180, 1),
            
            (1, 1, "Determinar el Orden",
             "¿Cuál es el orden de la ecuación: d²y/dx² + 3(dy/dx) - 2y = 0?",
             r"\frac{d^2y}{dx^2} + 3\frac{dy}{dx} - 2y = 0",
             "opcion_multiple",
             json.dumps(["2", "segundo", "orden 2", "segundo orden"]),
             json.dumps(["1 - Primer orden", "2 - Segundo orden", "3 - Tercer orden", "4 - Cuarto orden"]),
             "El orden es la derivada más alta que aparece.",
             "El orden es 2 porque la derivada más alta es d²y/dx² (segunda derivada).",
             20, 120, 2),
            
            (1, 1, "Lineal vs No Lineal",
             "¿La ecuación y' + y² = x es lineal o no lineal?",
             r"y' + y^2 = x",
             "opcion_multiple",
             json.dumps(["no lineal", "no-lineal", "nolineal"]),
             json.dumps(["Lineal", "No lineal"]),
             "En una EDO lineal, y y sus derivadas aparecen con exponente 1.",
             "NO es lineal porque y aparece elevada al cuadrado (y²).",
             25, 120, 3),
            
            (1, 1, "Clasificar EDO",
             "Clasifica la ecuación: y''' + 2y'' - y' + 3y = sin(x)",
             r"y''' + 2y'' - y' + 3y = \sin(x)",
             "texto",
             json.dumps(["lineal tercer orden", "tercer orden lineal", "lineal de tercer orden", "3er orden lineal"]),
             None,
             "Verifica el orden (derivada más alta) y si es lineal (exponentes de y).",
             "Es una EDO Lineal de Tercer Orden. Lineal porque y y sus derivadas tienen exponente 1.",
             30, 180, 4),
            
            # =====================================================
            # CATEGORÍA 2: Derivadas Básicas (Principiante)
            # =====================================================
            (2, 1, "Derivada de Potencia",
             "Calcula la derivada de f(x) = x⁵",
             r"f(x) = x^5",
             "texto",
             json.dumps(["5x^4", "5x⁴", "5*x^4", "5x4"]),
             None,
             "Usa la regla de la potencia: d/dx[xⁿ] = n·xⁿ⁻¹",
             "f'(x) = 5x⁴ (bajamos el exponente y restamos 1)",
             15, 60, 1),
            
            (2, 1, "Derivada de e^x",
             "Calcula la derivada de f(x) = e^x",
             r"f(x) = e^x",
             "texto",
             json.dumps(["e^x", "ex", "e^(x)"]),
             None,
             "La derivada de e^x es especial...",
             "f'(x) = e^x (la exponencial es su propia derivada)",
             15, 60, 2),
            
            (2, 1, "Derivada de sin(x)",
             "Calcula la derivada de f(x) = sin(x)",
             r"f(x) = \sin(x)",
             "texto",
             json.dumps(["cos(x)", "cosx", "cos x"]),
             None,
             "Recuerda las derivadas trigonométricas básicas.",
             "f'(x) = cos(x)",
             15, 60, 3),
            
            (2, 2, "Regla del Producto",
             "Calcula la derivada de f(x) = x² · e^x",
             r"f(x) = x^2 \cdot e^x",
             "texto",
             json.dumps(["2xe^x + x^2e^x", "e^x(2x+x^2)", "e^x(x^2+2x)", "(2x+x^2)e^x"]),
             None,
             "Usa la regla del producto: (uv)' = u'v + uv'",
             "f'(x) = 2x·e^x + x²·e^x = e^x(2x + x²)",
             25, 120, 4),
            
            (2, 2, "Regla de la Cadena",
             "Calcula la derivada de f(x) = sin(3x)",
             r"f(x) = \sin(3x)",
             "texto",
             json.dumps(["3cos(3x)", "3cos3x", "3·cos(3x)"]),
             None,
             "Usa la regla de la cadena: deriva la función exterior y multiplica por la derivada interior.",
             "f'(x) = cos(3x) · 3 = 3cos(3x)",
             25, 90, 5),
            
            # =====================================================
            # CATEGORÍA 3: Integrales Básicas (Principiante)
            # =====================================================
            (3, 1, "Integral de Potencia",
             "Calcula ∫x³ dx",
             r"\int x^3 \, dx",
             "texto",
             json.dumps(["x^4/4 + C", "x⁴/4 + C", "(x^4)/4 + C", "1/4 x^4 + C"]),
             None,
             "Usa la regla de la potencia inversa: ∫xⁿdx = xⁿ⁺¹/(n+1) + C",
             "∫x³dx = x⁴/4 + C",
             15, 60, 1),
            
            (3, 1, "Integral de e^x",
             "Calcula ∫e^x dx",
             r"\int e^x \, dx",
             "texto",
             json.dumps(["e^x + C", "e^x+C", "ex + C"]),
             None,
             "La integral de e^x es...",
             "∫e^x dx = e^x + C",
             15, 60, 2),
            
            (3, 1, "Integral de 1/x",
             "Calcula ∫(1/x) dx",
             r"\int \frac{1}{x} \, dx",
             "texto",
             json.dumps(["ln|x| + C", "ln(x) + C", "lnx + C", "ln|x|+C"]),
             None,
             "Esta es una integral fundamental.",
             "∫(1/x)dx = ln|x| + C",
             20, 60, 3),
            
            (3, 2, "Integral por Sustitución",
             "Calcula ∫2x·e^(x²) dx",
             r"\int 2x \cdot e^{x^2} \, dx",
             "texto",
             json.dumps(["e^(x^2) + C", "e^(x²) + C", "e^x² + C"]),
             None,
             "Intenta u = x², entonces du = 2x dx",
             "Con u = x², du = 2x dx: ∫e^u du = e^u + C = e^(x²) + C",
             30, 180, 4),
            
            # =====================================================
            # CATEGORÍA 4: Variables Separables (Básico)
            # =====================================================
            (4, 2, "Identificar Separable",
             "¿La ecuación dy/dx = xy es de variables separables?",
             r"\frac{dy}{dx} = xy",
             "opcion_multiple",
             json.dumps(["sí", "si", "yes"]),
             json.dumps(["Sí, es separable", "No, no es separable"]),
             "Una ecuación es separable si se puede escribir como dy/dx = f(x)·g(y)",
             "SÍ es separable: dy/dx = x · y, donde f(x)=x y g(y)=y",
             20, 90, 1),
            
            (4, 2, "Separar Variables",
             "Separa las variables en: dy/dx = x/y",
             r"\frac{dy}{dx} = \frac{x}{y}",
             "texto",
             json.dumps(["y dy = x dx", "ydy = xdx", "y·dy = x·dx"]),
             None,
             "Multiplica ambos lados por y y por dx.",
             "Separando: y dy = x dx",
             25, 120, 2),
            
            (4, 2, "Resolver EDO Separable",
             "Resuelve: dy/dx = x/y (encuentra la solución general)",
             r"\frac{dy}{dx} = \frac{x}{y}",
             "texto",
             json.dumps(["y^2 = x^2 + C", "y² = x² + C", "y^2 - x^2 = C", "y^2=x^2+C"]),
             None,
             "Separa variables e integra ambos lados.",
             "∫y dy = ∫x dx → y²/2 = x²/2 + C₁ → y² = x² + C",
             35, 240, 3),
            
            (4, 3, "EDO Separable Completa",
             "Resuelve: dy/dx = y·cos(x), con y(0) = 1",
             r"\frac{dy}{dx} = y \cdot \cos(x), \quad y(0) = 1",
             "texto",
             json.dumps(["y = e^sin(x)", "y = e^(sin x)", "y=e^sinx"]),
             None,
             "Separa: dy/y = cos(x)dx, integra y aplica condición inicial.",
             "∫dy/y = ∫cos(x)dx → ln|y| = sin(x) + C\nCon y(0)=1: ln(1) = sin(0) + C → C = 0\nSolución: y = e^(sin x)",
             45, 300, 4),
            
            # =====================================================
            # CATEGORÍA 5: EDOs Lineales 1er Orden (Básico)
            # =====================================================
            (5, 2, "Identificar P(x) y Q(x)",
             "En y' + 2y = e^x, identifica P(x) y Q(x)",
             r"y' + 2y = e^x",
             "texto",
             json.dumps(["P(x)=2, Q(x)=e^x", "P=2, Q=e^x", "2, e^x", "P(x) = 2, Q(x) = e^x"]),
             None,
             "La forma estándar es y' + P(x)y = Q(x)",
             "P(x) = 2 (coeficiente de y)\nQ(x) = e^x (término independiente)",
             25, 120, 1),
            
            (5, 2, "Factor Integrante",
             "Calcula el factor integrante μ(x) para: y' + 2y = e^x",
             r"y' + 2y = e^x",
             "texto",
             json.dumps(["e^(2x)", "e^2x", "e^{2x}"]),
             None,
             "μ(x) = e^(∫P(x)dx)",
             "μ(x) = e^(∫2dx) = e^(2x)",
             30, 180, 2),
            
            (5, 3, "Resolver EDO Lineal",
             "Resuelve: y' + 2y = e^x",
             r"y' + 2y = e^x",
             "texto",
             json.dumps(["y = e^x/3 + Ce^(-2x)", "y = (e^x)/3 + Ce^{-2x}", "y = e^x/3 + C·e^(-2x)"]),
             None,
             "Usa el factor integrante μ = e^(2x).",
             "μ = e^(2x)\nMultiplicando: e^(2x)y' + 2e^(2x)y = e^(3x)\n(e^(2x)y)' = e^(3x)\ne^(2x)y = e^(3x)/3 + C\ny = e^x/3 + Ce^(-2x)",
             50, 360, 3),
            
            # =====================================================
            # CATEGORÍA 6: Ecuaciones Exactas (Intermedio)
            # =====================================================
            (6, 3, "Verificar Exactitud",
             "¿Es exacta la ecuación (2xy + 3)dx + (x² + 4y)dy = 0?",
             r"(2xy + 3)dx + (x^2 + 4y)dy = 0",
             "opcion_multiple",
             json.dumps(["sí", "si", "es exacta"]),
             json.dumps(["Sí, es exacta", "No, no es exacta"]),
             "Verifica si ∂M/∂y = ∂N/∂x",
             "M = 2xy + 3, N = x² + 4y\n∂M/∂y = 2x, ∂N/∂x = 2x\nComo son iguales, SÍ es exacta.",
             35, 180, 1),
            
            (6, 3, "Encontrar ∂M/∂y",
             "Para (x²y + y³)dx + (x³ + 3xy²)dy = 0, calcula ∂M/∂y",
             r"(x^2y + y^3)dx + (x^3 + 3xy^2)dy = 0",
             "texto",
             json.dumps(["x^2 + 3y^2", "x² + 3y²", "3y^2 + x^2"]),
             None,
             "M = x²y + y³, deriva respecto a y.",
             "∂M/∂y = ∂(x²y + y³)/∂y = x² + 3y²",
             30, 120, 2),
            
            # =====================================================
            # CATEGORÍA 7: EDOs Homogéneas 2do Orden (Intermedio)
            # =====================================================
            (7, 3, "Ecuación Característica",
             "Escribe la ecuación característica de: y'' + 5y' + 6y = 0",
             r"y'' + 5y' + 6y = 0",
             "texto",
             json.dumps(["r^2 + 5r + 6 = 0", "r² + 5r + 6 = 0", "m^2 + 5m + 6 = 0"]),
             None,
             "Sustituye y = e^(rx), y' = re^(rx), y'' = r²e^(rx)",
             "La ecuación característica es: r² + 5r + 6 = 0",
             25, 120, 1),
            
            (7, 3, "Raíces Características",
             "Encuentra las raíces de r² + 5r + 6 = 0",
             r"r^2 + 5r + 6 = 0",
             "texto",
             json.dumps(["r = -2, -3", "r=-2,-3", "-2 y -3", "-2, -3"]),
             None,
             "Factoriza o usa la fórmula cuadrática.",
             "(r + 2)(r + 3) = 0 → r₁ = -2, r₂ = -3",
             25, 120, 2),
            
            (7, 3, "Solución General (Raíces Reales Distintas)",
             "Escribe la solución general de y'' + 5y' + 6y = 0",
             r"y'' + 5y' + 6y = 0",
             "texto",
             json.dumps(["y = C1·e^(-2x) + C2·e^(-3x)", "y = C1e^{-2x} + C2e^{-3x}", "C1e^(-2x) + C2e^(-3x)"]),
             None,
             "Las raíces son -2 y -3. Usa la forma y = C₁e^(r₁x) + C₂e^(r₂x)",
             "y = C₁e^(-2x) + C₂e^(-3x)",
             40, 240, 3),
            
            (7, 4, "Raíces Complejas",
             "Resuelve: y'' + 4y = 0",
             r"y'' + 4y = 0",
             "texto",
             json.dumps(["y = C1·cos(2x) + C2·sin(2x)", "C1cos(2x) + C2sin(2x)", "y = C1cos2x + C2sin2x"]),
             None,
             "r² + 4 = 0 → r = ±2i. Usa y = e^(αx)[C₁cos(βx) + C₂sin(βx)]",
             "r² = -4 → r = ±2i\nα = 0, β = 2\ny = C₁cos(2x) + C₂sin(2x)",
             45, 300, 4),
        ]
        
        cursor.executemany("""
            INSERT INTO ejercicios (
                categoria_id, nivel_id, titulo, problema, ecuacion_latex,
                tipo_respuesta, respuestas_correctas, opciones, pista, explicacion,
                xp_base, tiempo_limite_segundos, orden
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, ejercicios)
    
    # ========================
    # MÉTODOS DE USUARIO
    # ========================
    
    def create_user(self, username: str, password: str, email: str = None, nombre: str = None) -> Optional[int]:
        """Crea un nuevo usuario."""
        if not self.connection:
            return None
        
        cursor = self.connection.cursor()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            cursor.execute("""
                INSERT INTO usuarios (username, password_hash, email, nombre)
                VALUES (%s, %s, %s, %s)
            """, (username, password_hash, email, nombre))
            
            user_id = cursor.lastrowid
            
            # Crear registro de progreso
            cursor.execute("""
                INSERT INTO progreso_usuario (usuario_id) VALUES (%s)
            """, (user_id,))
            
            # Desbloquear primera categoría
            cursor.execute("""
                INSERT INTO categorias_usuario (usuario_id, categoria_id, desbloqueado, unlocked_at)
                VALUES (%s, 1, TRUE, NOW())
            """, (user_id,))
            
            self.connection.commit()
            return user_id
        except Error as e:
            print(f"Error creando usuario: {e}")
            return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Autentica un usuario y retorna sus datos."""
        if not self.connection:
            return None
        
        cursor = self.connection.cursor(dictionary=True)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute("""
            SELECT u.*, p.total_xp, p.nivel, p.racha_actual, p.monedas
            FROM usuarios u
            LEFT JOIN progreso_usuario p ON u.id = p.usuario_id
            WHERE u.username = %s AND u.password_hash = %s
        """, (username, password_hash))
        
        user = cursor.fetchone()
        
        if user:
            # Actualizar last_login
            cursor.execute("UPDATE usuarios SET last_login = NOW() WHERE id = %s", (user['id'],))
            self.connection.commit()
        
        return user
    
    def get_or_create_default_user(self) -> int:
        """Obtiene o crea el usuario por defecto."""
        cursor = self.connection.cursor()
        
        cursor.execute("SELECT id FROM usuarios WHERE username = 'estudiante'")
        result = cursor.fetchone()
        
        if result:
            return result[0]
        else:
            return self.create_user("estudiante", "calcquest123", nombre="Estudiante")
    
    def get_or_create_test_user(self) -> int:
        """Alias para get_or_create_default_user."""
        return self.get_or_create_default_user()
    
    def get_achievements(self, user_id: int) -> List[Dict]:
        """Obtiene todos los logros con estado de desbloqueo."""
        if not self.connection:
            return []
        
        cursor = self.connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT l.*, 
                   CASE WHEN lu.id IS NOT NULL THEN TRUE ELSE FALSE END as desbloqueado,
                   DATE_FORMAT(lu.unlocked_at, '%%d/%%m/%%Y') as fecha_desbloqueo
            FROM logros l
            LEFT JOIN logros_usuario lu ON l.id = lu.logro_id AND lu.usuario_id = %s
            WHERE l.is_secret = FALSE OR lu.id IS NOT NULL
            ORDER BY lu.unlocked_at DESC, l.valor_condicion ASC
        """, (user_id,))
        
        achievements = cursor.fetchall()
        
        # Renombrar campos para compatibilidad
        for ach in achievements:
            ach['xp_reward'] = ach.get('xp_recompensa', 0)
        
        return achievements
    
    # ========================
    # MÉTODOS DE PROGRESO
    # ========================
    
    def get_user_progress(self, user_id: int) -> Optional[Dict]:
        """Obtiene el progreso completo del usuario."""
        if not self.connection:
            return None
        
        cursor = self.connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT p.*, u.username, u.nombre, u.avatar
            FROM progreso_usuario p
            JOIN usuarios u ON p.usuario_id = u.id
            WHERE p.usuario_id = %s
        """, (user_id,))
        
        return cursor.fetchone()
    
    def update_user_progress(self, user_id: int, xp_gained: int = 0, 
                            exercise_completed: bool = False,
                            equation_solved: bool = False) -> Dict:
        """Actualiza el progreso del usuario."""
        if not self.connection:
            return {}
        
        cursor = self.connection.cursor(dictionary=True)
        
        # Obtener progreso actual
        cursor.execute("SELECT * FROM progreso_usuario WHERE usuario_id = %s", (user_id,))
        progress = cursor.fetchone()
        
        if not progress:
            return {}
        
        new_xp = progress['total_xp'] + xp_gained
        new_level = 1 + (new_xp // 100)
        
        updates = {
            'total_xp': new_xp,
            'nivel': new_level,
        }
        
        if exercise_completed:
            updates['ejercicios_completados'] = progress['ejercicios_completados'] + 1
        
        if equation_solved:
            updates['ecuaciones_resueltas'] = progress['ecuaciones_resueltas'] + 1
        
        # Actualizar racha
        today = date.today()
        last_activity = progress['ultima_actividad']
        
        if last_activity is None:
            updates['racha_actual'] = 1
        elif last_activity == today:
            pass  # Ya se registró hoy
        elif (today - last_activity).days == 1:
            updates['racha_actual'] = progress['racha_actual'] + 1
        else:
            updates['racha_actual'] = 1
        
        if updates.get('racha_actual', 0) > progress['racha_maxima']:
            updates['racha_maxima'] = updates['racha_actual']
        
        updates['ultima_actividad'] = today
        
        # Construir y ejecutar UPDATE
        set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
        values = list(updates.values()) + [user_id]
        
        cursor.execute(f"""
            UPDATE progreso_usuario SET {set_clause} WHERE usuario_id = %s
        """, values)
        
        self.connection.commit()

        # Desbloquear categorías según nivel actual
        self._unlock_categories(user_id, new_level, cursor)
        
        # Verificar logros
        unlocked_achievements = self._check_achievements(user_id, cursor)
        
        return {
            'new_xp': new_xp,
            'new_level': new_level,
            'level_up': new_level > progress['nivel'],
            'unlocked_achievements': unlocked_achievements
        }

    def _unlock_categories(self, user_id: int, user_level: int, cursor):
        """Desbloquea categorías cuyo nivel requerido sea <= nivel actual."""
        cursor.execute("""
            INSERT INTO categorias_usuario (usuario_id, categoria_id, desbloqueado, unlocked_at)
            SELECT %s, c.id, TRUE, NOW()
            FROM categorias c
            WHERE c.nivel_requerido <= %s
              AND NOT EXISTS (
                  SELECT 1 FROM categorias_usuario cu 
                  WHERE cu.usuario_id = %s AND cu.categoria_id = c.id
              )
        """, (user_id, user_level, user_id))
        self.connection.commit()
    
    def _check_achievements(self, user_id: int, cursor) -> List[Dict]:
        """Verifica y desbloquea logros."""
        # Obtener progreso actual
        cursor.execute("SELECT * FROM progreso_usuario WHERE usuario_id = %s", (user_id,))
        progress = cursor.fetchone()
        
        # Obtener logros no desbloqueados
        cursor.execute("""
            SELECT l.* FROM logros l
            WHERE l.id NOT IN (
                SELECT logro_id FROM logros_usuario WHERE usuario_id = %s
            )
        """, (user_id,))
        
        pending_achievements = cursor.fetchall()
        unlocked = []
        
        for ach in pending_achievements:
            should_unlock = False
            
            if ach['tipo_condicion'] == 'xp' and progress['total_xp'] >= ach['valor_condicion']:
                should_unlock = True
            elif ach['tipo_condicion'] == 'racha' and progress['racha_actual'] >= ach['valor_condicion']:
                should_unlock = True
            elif ach['tipo_condicion'] == 'ejercicios' and progress['ejercicios_completados'] >= ach['valor_condicion']:
                should_unlock = True
            
            if should_unlock:
                cursor.execute("""
                    INSERT INTO logros_usuario (usuario_id, logro_id) VALUES (%s, %s)
                """, (user_id, ach['id']))
                
                # Dar XP de recompensa
                cursor.execute("""
                    UPDATE progreso_usuario SET total_xp = total_xp + %s WHERE usuario_id = %s
                """, (ach['xp_recompensa'], user_id))
                
                unlocked.append({
                    'id': ach['id'],
                    'nombre': ach['nombre'],
                    'descripcion': ach['descripcion'],
                    'icono': ach['icono'],
                    'xp_recompensa': ach['xp_recompensa']
                })
        
        self.connection.commit()
        return unlocked
    
    # ========================
    # MÉTODOS DE EJERCICIOS
    # ========================
    
    def get_categories(self, user_id: int = None) -> List[Dict]:
        """Obtiene todas las categorías con su estado de desbloqueo."""
        if not self.connection:
            return []
        
        cursor = self.connection.cursor(dictionary=True)
        
        if user_id:
            cursor.execute("""
                SELECT c.*, 
                       COALESCE(cu.desbloqueado, FALSE) as desbloqueado,
                       COALESCE(cu.progreso_porcentaje, 0) as progreso,
                       (SELECT COUNT(*) FROM ejercicios e WHERE e.categoria_id = c.id) as total_ejercicios,
                       (SELECT COUNT(*) FROM progreso_ejercicios pe 
                        JOIN ejercicios e ON pe.ejercicio_id = e.id 
                        WHERE e.categoria_id = c.id AND pe.usuario_id = %s AND pe.completado = TRUE) as ejercicios_completados
                FROM categorias c
                LEFT JOIN categorias_usuario cu ON c.id = cu.categoria_id AND cu.usuario_id = %s
                WHERE c.is_active = TRUE
                ORDER BY c.orden
            """, (user_id, user_id))
        else:
            cursor.execute("""
                SELECT c.*, 
                       (SELECT COUNT(*) FROM ejercicios e WHERE e.categoria_id = c.id) as total_ejercicios
                FROM categorias c
                WHERE c.is_active = TRUE
                ORDER BY c.orden
            """)
        
        return cursor.fetchall()
    
    def get_exercises_by_category(self, categoria_id: int, user_id: int = None) -> List[Dict]:
        """Obtiene ejercicios de una categoría."""
        if not self.connection:
            return []
        
        cursor = self.connection.cursor(dictionary=True)
        
        if user_id:
            cursor.execute("""
                SELECT e.*, n.nombre as nivel_nombre, n.color as nivel_color, n.icono as nivel_icono,
                       n.multiplicador_xp,
                       COALESCE(pe.completado, FALSE) as completado,
                       COALESCE(pe.intentos, 0) as intentos,
                       pe.mejor_tiempo_segundos,
                       pe.xp_ganado
                FROM ejercicios e
                JOIN niveles_dificultad n ON e.nivel_id = n.id
                LEFT JOIN progreso_ejercicios pe ON e.id = pe.ejercicio_id AND pe.usuario_id = %s
                WHERE e.categoria_id = %s AND e.is_active = TRUE
                ORDER BY e.orden
            """, (user_id, categoria_id))
        else:
            cursor.execute("""
                SELECT e.*, n.nombre as nivel_nombre, n.color as nivel_color, n.icono as nivel_icono
                FROM ejercicios e
                JOIN niveles_dificultad n ON e.nivel_id = n.id
                WHERE e.categoria_id = %s AND e.is_active = TRUE
                ORDER BY e.orden
            """, (categoria_id,))
        
        exercises = cursor.fetchall()
        
        # Parsear JSON fields
        for ex in exercises:
            if ex.get('respuestas_correctas'):
                ex['respuestas_correctas'] = json.loads(ex['respuestas_correctas'])
            if ex.get('opciones'):
                ex['opciones'] = json.loads(ex['opciones'])
        
        return exercises
    
    def get_exercise_by_id(self, ejercicio_id: int) -> Optional[Dict]:
        """Obtiene un ejercicio por su ID."""
        if not self.connection:
            return None
        
        cursor = self.connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT e.*, n.nombre as nivel_nombre, n.color as nivel_color, 
                   n.icono as nivel_icono, n.multiplicador_xp,
                   c.nombre as categoria_nombre
            FROM ejercicios e
            JOIN niveles_dificultad n ON e.nivel_id = n.id
            JOIN categorias c ON e.categoria_id = c.id
            WHERE e.id = %s
        """, (ejercicio_id,))
        
        exercise = cursor.fetchone()
        
        if exercise:
            if exercise.get('respuestas_correctas'):
                exercise['respuestas_correctas'] = json.loads(exercise['respuestas_correctas'])
            if exercise.get('opciones'):
                exercise['opciones'] = json.loads(exercise['opciones'])
        
        return exercise
    
    def submit_exercise_answer(self, user_id: int, ejercicio_id: int, 
                               respuesta: str, tiempo_segundos: int = None,
                               is_validated: bool = False, xp_override: int = None,
                               attempts: int = None) -> Dict:
        """Registra la respuesta de un ejercicio.
        Si is_validated=True se asume que la respuesta ya fue validada en la UI y se usa xp_override."""
        if not self.connection:
            return {'success': False, 'error': 'No database connection'}
        
        cursor = self.connection.cursor(dictionary=True)
        
        # Obtener ejercicio
        exercise = self.get_exercise_by_id(ejercicio_id)
        if not exercise:
            return {'success': False, 'error': 'Exercise not found'}
        
        # Verificar respuesta (o confiar en validación previa)
        if is_validated:
            is_correct = True
        else:
            respuesta_normalizada = respuesta.strip().lower().replace(" ", "")
            is_correct = any(
                respuesta_normalizada == ans.lower().replace(" ", "")
                for ans in exercise.get('respuestas_correctas', [])
            )
        
        # Obtener progreso actual del ejercicio
        cursor.execute("""
            SELECT * FROM progreso_ejercicios 
            WHERE usuario_id = %s AND ejercicio_id = %s
        """, (user_id, ejercicio_id))
        current_progress = cursor.fetchone()
        
        xp_earned = 0
        first_time_correct = False
        
        if is_correct:
            if current_progress is None:
                # Primera vez completando
                first_time_correct = True
                xp_earned = xp_override if xp_override is not None else int(exercise['xp_base'] * float(exercise['multiplicador_xp']))
                intentos_val = attempts if attempts is not None else 1
                
                cursor.execute("""
                    INSERT INTO progreso_ejercicios 
                    (usuario_id, ejercicio_id, completado, intentos, mejor_tiempo_segundos, 
                     xp_ganado, primera_vez_correcto, completed_at)
                    VALUES (%s, %s, TRUE, %s, %s, %s, TRUE, NOW())
                """, (user_id, ejercicio_id, intentos_val, tiempo_segundos, xp_earned))
            elif not current_progress['completado']:
                # No lo había completado antes
                first_time_correct = True
                xp_earned = xp_override if xp_override is not None else int(exercise['xp_base'] * float(exercise['multiplicador_xp']) * 0.5)
                intentos_val = attempts if attempts is not None else current_progress['intentos'] + 1
                
                cursor.execute("""
                    UPDATE progreso_ejercicios 
                    SET completado = TRUE, intentos = %s, 
                        mejor_tiempo_segundos = LEAST(COALESCE(mejor_tiempo_segundos, 9999), %s),
                        xp_ganado = %s, completed_at = NOW(), primera_vez_correcto = TRUE
                    WHERE usuario_id = %s AND ejercicio_id = %s
                """, (intentos_val, tiempo_segundos, xp_earned, user_id, ejercicio_id))
            else:
                # Ya lo había completado, solo actualizar intentos
                intentos_val = attempts if attempts is not None else current_progress['intentos'] + 1
                cursor.execute("""
                    UPDATE progreso_ejercicios 
                    SET intentos = %s,
                        mejor_tiempo_segundos = LEAST(mejor_tiempo_segundos, %s)
                    WHERE usuario_id = %s AND ejercicio_id = %s
                """, (intentos_val, tiempo_segundos, user_id, ejercicio_id))
        else:
            # Respuesta incorrecta
            if current_progress is None:
                cursor.execute("""
                    INSERT INTO progreso_ejercicios 
                    (usuario_id, ejercicio_id, completado, intentos)
                    VALUES (%s, %s, FALSE, 1)
                """, (user_id, ejercicio_id))
            else:
                cursor.execute("""
                    UPDATE progreso_ejercicios 
                    SET intentos = intentos + 1
                    WHERE usuario_id = %s AND ejercicio_id = %s
                """, (user_id, ejercicio_id))
        
        self.connection.commit()
        
        # Actualizar progreso general si ganó XP
        progress_update = {}
        if xp_earned > 0:
            progress_update = self.update_user_progress(
                user_id, 
                xp_gained=xp_earned, 
                exercise_completed=first_time_correct
            )
        
        return {
            'success': True,
            'is_correct': is_correct,
            'xp_earned': xp_earned,
            'first_time': first_time_correct,
            'explanation': exercise.get('explicacion', ''),
            'progress_update': progress_update
        }
    
    def get_difficulty_levels(self) -> List[Dict]:
        """Obtiene todos los niveles de dificultad."""
        if not self.connection:
            return []
        
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM niveles_dificultad ORDER BY id")
        return cursor.fetchall()
    
    def get_user_achievements(self, user_id: int) -> Tuple[List[Dict], List[Dict]]:
        """Obtiene logros desbloqueados y pendientes."""
        if not self.connection:
            return [], []
        
        cursor = self.connection.cursor(dictionary=True)
        
        # Desbloqueados
        cursor.execute("""
            SELECT l.*, lu.unlocked_at
            FROM logros l
            JOIN logros_usuario lu ON l.id = lu.logro_id
            WHERE lu.usuario_id = %s
            ORDER BY lu.unlocked_at DESC
        """, (user_id,))
        unlocked = cursor.fetchall()
        
        # Pendientes (no secretos)
        cursor.execute("""
            SELECT l.*
            FROM logros l
            WHERE l.id NOT IN (
                SELECT logro_id FROM logros_usuario WHERE usuario_id = %s
            ) AND l.is_secret = FALSE
            ORDER BY l.valor_condicion
        """, (user_id,))
        pending = cursor.fetchall()
        
        return unlocked, pending
    
    def close(self):
        """Cierra la conexión."""
        if self.connection:
            self.connection.close()
            self.connection = None
