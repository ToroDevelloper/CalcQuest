# Instalar y ejecutar CalcQuest desde GitHub (Windows)

## Requisitos previos
- Windows 10/11.
- Git instalado y en PATH.
- Python 3.11+.
- MySQL Server en local (puerto 3306) y un usuario con permisos de creación de BD (por defecto `root` sin contraseña; ajusta según tu entorno).

## Pasos
1. **Clonar el repositorio**
   ```powershell
   git clone https://github.com/ToroDevelloper/CalcQuest.git
   cd CalcQuest
   ```

2. **Crear y activar entorno virtual**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

3. **Instalar dependencias**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configurar credenciales MySQL (si difieren del default)**
   - Abre `src/main.py` y en `init_database()` ajusta `host`, `user`, `password`, `database` a tu configuración.
   - Asegúrate de que el servicio MySQL esté iniciado.

5. **Ejecutar la aplicación**
   ```powershell
   python src/main.py
   ```
   - Al iniciar, se crea la base `calcquest` con tablas y datos iniciales si no existen.
   - Se crea/usa un usuario por defecto `estudiante`.

6. **(Opcional) Detener o limpiar**
   - Para salir, cierra la ventana de la app.
   - Para desactivar el entorno virtual: `deactivate`.

## Problemas comunes y soluciones
- **Error de conexión MySQL**: revisa credenciales, puerto 3306 abierto y servicio MySQL iniciado.
- **Faltan dependencias al ejecutar**: reinstala `pip install -r requirements.txt` con el entorno activado.
- **No sube nivel/XP**: completa ejercicios nuevos; cada 100 XP sube 1 nivel. El progreso se guarda en `progreso_usuario.total_xp`.

## Estructura relevante
- `src/main.py`: punto de entrada; configura la conexión MySQL.
- `src/core/mysql_database.py`: lógica de persistencia y XP/ niveles.
- `src/ui/`: vistas de PyQt6 (dashboard, ejercicios, progreso).
