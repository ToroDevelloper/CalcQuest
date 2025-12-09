# Documento de Diseño Técnico (TDD) - Aprende-E.D
**Asistente Personal Gamificado para Cálculo y Ecuaciones Diferenciales**
*(Versión 2.0 - Pivote a EdTech/Gamificación)*

**Autor:** Kilo Code (Arquitecto de Software Senior)
**Fecha:** 09 de Diciembre, 2025
**Filosofía:** "Matemáticas Divertidas para Principiantes Absolutos"

---

## 1. Visión del Producto y Filosofía UX

### 1.1 El Cambio de Paradigma
El objetivo ya no es ser una herramienta de "entrenamiento riguroso", sino un **Compañero de Viaje Amigable**. La aplicación debe sentirse como un juego móvil moderno (tipo Duolingo) pero con la potencia de un motor simbólico de escritorio.
*   **Público Objetivo:** Estudiantes con *cero* conocimiento previo o ansiedad matemática.
*   **Tono:** Alentador, conversacional, paciente. Nunca castigador.

### 1.2 Principios de Diseño UX
1.  **Atomic Learning:** Romper problemas complejos (ej. una E.D. lineal) en micro-pasos digeribles (1. Identificar P(x), 2. Integrar P(x), etc.).
2.  **Interfaz Invisible:** El usuario interactúa con un "Chatbot Tutor" o "Wizard", no con formularios de datos crudos.
3.  **Gamificación Core:** XP (Experiencia), Rachas (Streaks), Desbloqueo de Temas (Árbol de Habilidades).

---

## 2. Arquitectura del Sistema (PyQt6 + Gamification Engine)

### 2.1 Pila Tecnológica Refinada
*   **Frontend:** **PyQt6** con estilos avanzados (QSS) para emular interfaces web modernas (bordes redondeados, sombras suaves, animaciones).
*   **Visualización:** **Manim** (o Matplotlib muy estilizado) para animaciones matemáticas fluidas, no gráficas estáticas aburridas.
*   **Motor Lógico:**
    *   **SymPy:** Para resolución simbólica.
    *   **Step-Engine:** Nueva capa lógica que *intercepta* la solución de SymPy y la descompone en pasos explicativos en lenguaje natural.

### 2.2 Estructura de Módulos (Vistas)
La aplicación es una SPA (Single Page Application) de escritorio:

1.  **Dashboard (The Hub):**
    *   Estado del Jugador (Nivel, XP, Avatar).
    *   Mapa de Aventura (Ruta de aprendizaje lineal).
2.  **The Solver (Assistant Mode):**
    *   Interfaz tipo chat/wizard.
    *   El sistema "habla" primero: *"¡Hola! Vamos a resolver esta E.D. juntos. Primero, ¿puedes decirme cuál es el término que acompaña a la Y?"*
3.  **Concept Visualizer:**
    *   Playground interactivo. *"Mueve este deslizador para ver cómo cambia la pendiente"*.

---

## 3. Modelo de Datos para Gamificación

### 3.1 Esquema Actualizado (MySQL/SQLite)
Se añaden tablas para soportar mecánicas de juego:

*   **`user_progress`**:
    *   `current_streak` (días seguidos).
    *   `total_xp`.
    *   `currency` (monedas virtuales para personalizar avatar).
*   **`achievements`**:
    *   `id`, `name` (ej. "Calculadora Humana"), `condition_logic`.
*   **`skill_tree`**:
    *   `node_id`, `parent_node_id`, `is_unlocked`.

---

## 4. Algoritmos Pedagógicos

### 4.1 Motor "Step-by-Step"
A diferencia del diseño anterior (caja negra), este motor es esencial.
*   *Input:* `y' + 2y = e^x`
*   *Process:*
    1.  Detectar tipo: "Lineal Primer Orden".
    2.  Paso 1: Identificar $P(x)=2$. Generar explicación de texto.
    3.  Paso 2: Calcular Factor Integrante $\mu = e^{\int 2 dx}$.
    4.  Paso 3: Multiplicar ecuación.
*   *Output:* Lista secuencial de objetos `Step(latex, explanation, hint)`.

---

## 5. Estrategia de Interfaz (Mockup Specs)
El mockup HTML/CSS simulará esta experiencia de escritorio moderna:
*   **Colores:** Paleta vibrante pero suave (Violetas, Azules pastel, Blancos). Nada de "Gris Windows 95".
*   **Tipografía:** Sans-serif redondeada (ej. Nunito, Quicksand) para amabilidad.
*   **Navegación:** Barra lateral icónica simple o Bottom Bar tipo app móvil.