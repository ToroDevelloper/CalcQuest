# Guía de Ejecución - CalcQuest

## Requisitos Previos
1.  Python 3.10+
2.  Entorno virtual recomendado

## Instalación
```bash
pip install -r requirements.txt
```

## Ejecución de Pruebas (TDD Verification)
Para verificar que todos los módulos cumplen con las especificaciones del diseño:
```bash
pytest
```
*Esto ejecutará las suites de pruebas para Gamificación, Motor Lógico e Interfaz Gráfica.*

## Iniciar la Aplicación
```bash
python src/main.py
```

## Estructura del Proyecto
*   **src/core:** Lógica de negocio (Gamificación, Usuario).
*   **src/engine:** Motor matemático y de pasos (SymPy wrapper).
*   **src/ui:** Vistas y componentes de PyQt6.
*   **tests/:** Pruebas unitarias e integración correspondientes a cada módulo.

## Estado Actual
*   [x] Modelo de datos de gamificación implementado y probado.
*   [x] Motor de pasos básico (StepEngine) con detección de E.D. lineales.
*   [x] Interfaz gráfica principal (MainWindow) con estructura de Sidebar/Content.
*   [x] Vista "Solver" tipo chat implementada funcionalmente.