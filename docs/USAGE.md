# Cómo usar CalcQuest (Aplicación de escritorio)

## Requisitos previos
- Windows 10/11.
- Python 3.11+ (recomendado).
- MySQL Server en local (puerto 3306 por defecto) con usuario que tenga permisos de creación de BD/tablas.
- Dependencias de Python instaladas desde `requirements.txt` dentro de un entorno virtual (ver guía de instalación).

## Inicio rápido (ya instalado)
1. Activa el entorno virtual: `\.venv\Scripts\activate`
2. Ejecuta la app: `python src/main.py`
3. La app crea/usa la BD `calcquest` y un usuario por defecto `estudiante`.
4. Al abrir verás el Dashboard. Usa el sidebar para navegar:
   - "Ejercicios": resuelve ejercicios, gana XP.
   - "Mi Progreso": revisa nivel, XP total, racha y logros.
   - "Solucionador" y "Graficador": herramientas auxiliares.

## Flujo de uso recomendado
- Entra a "Ejercicios" y elige una categoría desbloqueada.
- Resuelve ejercicios; al acertar se otorga XP y se marcan completados.
- Cada 100 XP subes de nivel; esto desbloquea más categorías automáticamente.
- Revisa "Mi Progreso" para ver barra de nivel, XP total, racha y logros.

## Consejos y notas
- Las respuestas aceptan equivalencias sencillas (mayúsculas/minúsculas y espacios no importan).
- Si MySQL no está disponible, la app seguirá en modo sin BD, pero el progreso no se guardará.
- Para cerrar la app, simplemente cierra la ventana principal.

## Problemas comunes
- **La app no abre o muestra error de MySQL**: verifica que el servicio MySQL está iniciado y las credenciales en `src/main.py` (función `init_database`) son correctas.
- **No sube nivel o XP**: asegúrate de completar ejercicios por primera vez; cada acierto otorga XP y se suma a `total_xp`.
- **No se desbloquean categorías**: se desbloquean al alcanzar el nivel requerido; se recalculan en cada actualización de progreso.
