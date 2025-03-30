# Comandos Shell desde G-Code (Extendido)

Este módulo permite ejecutar comandos shell desde la interfaz de G-Code de Klipper, con características avanzadas de seguridad, registro y configuración. Desarrollado originalmente por [Arksine](https://github.com/Arksine), esta extensión proporciona una forma potente y segura de interactuar con el sistema operativo desde su impresora 3D.

## Características Principales

- **Ejecución de comandos**: Ejecute cualquier comando shell válido desde la interfaz de G-Code
- **Control de tiempo de espera**: Protección contra comandos que no responden
- **Modo detallado**: Visualización de la salida del comando en tiempo real
- **Seguridad mejorada**: Restricción de parámetros mediante patrones regex
- **Registro de comandos**: Historial detallado de ejecuciones con códigos de salida
- **Entorno personalizable**: Directorio de trabajo y variables de entorno configurables
- **Manejo de errores**: Detección y notificación de fallos en la ejecución
- **Codificación universal**: Soporte para diferentes codificaciones de caracteres

## Configuración Completa

Aquí hay un ejemplo de configuración completa con todas las opciones disponibles:

```ini
[gcode_shell_command mi_comando]
command: echo "Hola Mundo"          # Comando shell a ejecutar (obligatorio)
timeout: 5.0                        # Tiempo máximo de ejecución en segundos (predeterminado: 2.0)
verbose: True                       # Mostrar salida del comando (predeterminado: True)

# Opciones de seguridad
allow_any_params: False             # Permitir cualquier parámetro (predeterminado: False)
allowed_params_pattern: ^[\w\-\.]+$ # Patrón regex para parámetros permitidos

# Opciones de registro
enable_logging: True                # Habilitar registro de comandos (predeterminado: False)
max_history: 20                     # Número máximo de entradas en el historial (predeterminado: 10)

# Opciones de entorno
working_dir: ~/printer_data         # Directorio de trabajo para el comando
env_vars: VAR1=valor1 VAR2=valor2  # Variables de entorno para el comando
```

### Explicación Detallada de Opciones

#### Opciones Básicas

- **command**: El comando shell a ejecutar. Puede incluir argumentos fijos. Se expanden rutas con `~` (obligatorio).
- **timeout**: Tiempo máximo en segundos que puede ejecutarse el comando antes de ser terminado (predeterminado: 2.0).
- **verbose**: Si está activado, la salida del comando se mostrará en la consola de Klipper (predeterminado: True).

#### Opciones de Seguridad

- **allow_any_params**: Si está activado, permite pasar cualquier parámetro al comando (predeterminado: False).
- **allowed_params_pattern**: Patrón de expresión regular que deben cumplir los parámetros para ser aceptados. Solo se aplica si `allow_any_params` es False.

#### Opciones de Registro

- **enable_logging**: Activa el registro del historial de ejecuciones del comando (predeterminado: False).
- **max_history**: Número máximo de entradas en el historial (predeterminado: 10, máximo: 100).

#### Opciones de Entorno

- **working_dir**: Directorio de trabajo donde se ejecutará el comando. Útil para comandos que operan sobre archivos específicos.
- **env_vars**: Variables de entorno para el comando en formato `VARIABLE=valor`. Múltiples variables se separan con espacios.

## Comandos G-Code

### RUN_SHELL_COMMAND

Ejecuta un comando shell configurado.

```gcode
RUN_SHELL_COMMAND CMD=mi_comando [PARAMS="param1 param2 ..."]
```

- `CMD`: Nombre del comando shell configurado (obligatorio)
- `PARAMS`: Parámetros adicionales para pasar al comando (opcional)

### SHELL_COMMAND_HISTORY

Muestra el historial de comandos ejecutados (solo disponible si `enable_logging` está activado).

```gcode
SHELL_COMMAND_HISTORY CMD=mi_comando [COUNT=5]
```

- `CMD`: Nombre del comando shell configurado (obligatorio)
- `COUNT`: Número de entradas del historial a mostrar (opcional, predeterminado: todas)

## Características de Seguridad Avanzadas

### Restricción de Parámetros

Para mejorar la seguridad, puede restringir qué parámetros se permiten pasar a un comando:

1. **Sin parámetros**: Si `allow_any_params` es `False` y no se especifica `allowed_params_pattern`, no se permitirán parámetros.

2. **Parámetros con patrón**: Si se especifica `allowed_params_pattern`, solo se permitirán parámetros que coincidan con el patrón regex.

3. **Cualquier parámetro**: Si `allow_any_params` es `True`, se permitirán todos los parámetros (no recomendado para comandos sensibles).

### Ejemplos de Patrones de Seguridad

- Solo alfanuméricos: `^[a-zA-Z0-9]+$`
- Alfanuméricos con guiones y puntos: `^[\w\-\.]+$`
- Rutas de archivo seguras: `^[\w\-\./]+$`
- Números enteros positivos: `^[0-9]+$`
- Nombres de archivo válidos: `^[\w\-\.]+\.[a-zA-Z0-9]+$`

### Mejores Prácticas de Seguridad

- **Principio de mínimo privilegio**: Configure cada comando con los mínimos permisos necesarios.
- **Validación estricta**: Use patrones regex específicos en lugar de permitir cualquier parámetro.
- **Evite comandos peligrosos**: No configure comandos que puedan dañar el sistema o exponer información sensible.
- **Limite el tiempo de ejecución**: Use tiempos de espera cortos para evitar bloqueos.
- **Revise los registros**: Monitoree regularmente el historial de comandos para detectar usos indebidos.

## Sistema de Registro Detallado

Cuando `enable_logging` está activado, el módulo registra información detallada sobre cada ejecución de comando:

- **Timestamp**: Fecha y hora exacta de la ejecución
- **Parámetros**: Parámetros utilizados en la ejecución
- **Código de salida**: Código de retorno del comando (0 generalmente indica éxito)
- **Duración**: Tiempo que tardó en ejecutarse el comando
- **Estado de timeout**: Indica si el comando agotó el tiempo de espera

Esta información es invaluable para depurar problemas y monitorear el uso de comandos.

### Formato del Historial

El historial se muestra en el siguiente formato:

```
Command history for [nombre_comando] (last [count] entries):
1. [YYYY-MM-DD HH:MM:SS] Params: param1 param2 | Status: EXIT 0 | Duration: 0.25s
2. [YYYY-MM-DD HH:MM:SS] Params: (none) | Status: TIMEOUT | Duration: 2.00s
```

## Entorno de Ejecución Personalizado

### Directorio de Trabajo

Puede especificar un directorio de trabajo personalizado con la opción `working_dir`. Esto es útil para comandos que necesitan ejecutarse en un directorio específico, como scripts que operan sobre archivos locales.

```ini
[gcode_shell_command backup_configs]
command: tar -czf backup.tar.gz *.cfg
working_dir: ~/printer_data/config
```

### Variables de Entorno

La opción `env_vars` permite definir variables de entorno específicas para el comando. El formato es `VARIABLE=valor` con múltiples variables separadas por espacios.

```ini
[gcode_shell_command notify_print_done]
command: ./send_notification.sh
env_vars: PRINTER_NAME=Ender3 NOTIFY_LEVEL=info API_KEY=abc123
working_dir: ~/scripts
```

## Manejo de Errores y Salida

### Códigos de Salida

Los comandos shell devuelven códigos de salida que indican el resultado de la ejecución:

- **0**: Éxito (la mayoría de los comandos)
- **Distinto de 0**: Error (el significado específico depende del comando)

### Timeout y Terminación

Si un comando no completa su ejecución dentro del tiempo especificado en `timeout`:

1. El sistema intentará terminar el proceso de forma ordenada (SIGTERM)
2. Si no responde, forzará su finalización (SIGKILL)
3. Se registrará como TIMEOUT en el historial
4. Se mostrará un mensaje indicando que el comando agotó el tiempo de espera

### Manejo de Codificación

El módulo maneja automáticamente diferentes codificaciones de caracteres:

1. Intenta decodificar la salida como UTF-8
2. Si falla, utiliza la codificación predeterminada del sistema
3. Aplica reemplazo de caracteres no válidos para evitar errores

## Ejemplos Prácticos Avanzados

### Monitoreo de Temperatura del Sistema

```ini
[gcode_shell_command check_temp]
command: sensors | grep "CPU Temperature"
timeout: 3.
verbose: True
enable_logging: True

[gcode_macro CHECK_SYSTEM_TEMP]
gcode:
    RUN_SHELL_COMMAND CMD=check_temp
```

### Backup Automático de Configuraciones

```ini
[gcode_shell_command backup_configs]
command: tar -czf config_backup_$(date +%Y%m%d_%H%M%S).tar.gz *.cfg
timeout: 10.
verbose: True
working_dir: ~/printer_data/config

[gcode_macro BACKUP_CONFIGS]
gcode:
    RUN_SHELL_COMMAND CMD=backup_configs
```

### Notificación de Finalización de Impresión

```ini
[gcode_shell_command send_notification]
command: ./notify.sh
timeout: 5.
verbose: False
allow_any_params: True
env_vars: NOTIFY_SERVICE=telegram
working_dir: ~/scripts

[gcode_macro PRINT_DONE_NOTIFY]
gcode:
    RUN_SHELL_COMMAND CMD=send_notification PARAMS="Print complete: {printer.print_stats.filename}"
```

### Control de Iluminación Externa

```ini
[gcode_shell_command control_lights]
command: python control_lights.py
timeout: 2.
verbose: True
allow_any_params: False
allowed_params_pattern: ^(on|off|toggle|[0-9]{1,3})$

[gcode_macro LIGHTS_ON]
gcode:
    RUN_SHELL_COMMAND CMD=control_lights PARAMS="on"

[gcode_macro LIGHTS_OFF]
gcode:
    RUN_SHELL_COMMAND CMD=control_lights PARAMS="off"

[gcode_macro LIGHTS_TOGGLE]
gcode:
    RUN_SHELL_COMMAND CMD=control_lights PARAMS="toggle"

[gcode_macro SET_BRIGHTNESS]
gcode:
    {% set LEVEL = params.LEVEL|default(100)|int %}
    {% if LEVEL < 0 or LEVEL > 100 %}
        { action_respond_info("Brightness must be between 0 and 100") }
    {% else %}
        RUN_SHELL_COMMAND CMD=control_lights PARAMS="{LEVEL}"
    {% endif %}
```

### Monitoreo de Espacio en Disco

```ini
[gcode_shell_command check_disk_space]
command: df -h /
timeout: 3.
verbose: True

[gcode_macro CHECK_DISK]
gcode:
    RUN_SHELL_COMMAND CMD=check_disk_space
```

### Ejecución de Scripts Personalizados con Parámetros

```ini
[gcode_shell_command run_script]
command: python ~/scripts/custom_script.py
timeout: 10.
verbose: True
allow_any_params: False
allowed_params_pattern: ^[a-zA-Z0-9_\-\.]+$

[gcode_macro RUN_CUSTOM_SCRIPT]
gcode:
    {% set SCRIPT_NAME = params.SCRIPT|default("") %}
    {% if SCRIPT_NAME %}
        RUN_SHELL_COMMAND CMD=run_script PARAMS="{SCRIPT_NAME}"
    {% else %}
        { action_respond_info("Error: Script name required") }
    {% endif %}
```

## Integración con Otras Funcionalidades de Klipper

### Uso con Variables de Klipper

```ini
[gcode_shell_command log_temps]
command: echo
timeout: 2.
verbose: True
allow_any_params: True
enable_logging: True

[gcode_macro LOG_TEMPERATURES]
gcode:
    {% set bed_temp = printer.heater_bed.temperature %}
    {% set extruder_temp = printer.extruder.temperature %}
    {% set timestamp = printer.system_stats.ctime %}
    RUN_SHELL_COMMAND CMD=log_temps PARAMS="{timestamp}: Bed: {bed_temp}, Extruder: {extruder_temp}"
```

### Ejecución Condicional Basada en Estado de la Impresora

```ini
[gcode_shell_command system_maintenance]
command: ~/scripts/maintenance.sh
timeout: 30.
verbose: True

[gcode_macro MAINTENANCE_CHECK]
gcode:
    {% if printer.idle_timeout.state == "Idle" %}
        { action_respond_info("Ejecutando mantenimiento del sistema...") }
        RUN_SHELL_COMMAND CMD=system_maintenance
    {% else %}
        { action_respond_info("Error: La impresora debe estar inactiva para el mantenimiento") }
    {% endif %}
```

## Consejos y Solución de Problemas

### Problemas Comunes y Soluciones

#### El comando agota el tiempo de espera

- **Problema**: El comando siempre termina con TIMEOUT
- **Solución**: Aumente el valor de `timeout` o verifique si el comando está bloqueado esperando entrada del usuario

#### Error de permisos

- **Problema**: El comando falla con errores de permisos
- **Solución**: Verifique que el usuario que ejecuta Klipper tenga permisos para ejecutar el comando o script

#### Parámetros rechazados

- **Problema**: Los parámetros son rechazados aunque parecen válidos
- **Solución**: Verifique que el patrón regex en `allowed_params_pattern` sea correcto y pruebe el patrón con los parámetros que desea usar

#### La salida no se muestra

- **Problema**: El comando se ejecuta pero no se ve ninguna salida
- **Solución**: Asegúrese de que `verbose` esté configurado como `True`

#### Errores de codificación

- **Problema**: Caracteres extraños en la salida del comando
- **Solución**: Asegúrese de que los scripts generen salida en UTF-8 o en la codificación predeterminada del sistema

### Optimización de Rendimiento

- **Comandos rápidos**: Para comandos que se ejecutan frecuentemente y rápidamente, considere desactivar `verbose` para reducir la sobrecarga
- **Historial limitado**: Para comandos ejecutados muy frecuentemente, mantenga `max_history` en un valor bajo o desactive `enable_logging`
- **Tiempos de espera apropiados**: Configure `timeout` según el tiempo esperado de ejecución del comando para evitar esperas innecesarias

### Depuración Avanzada

- Utilice el historial de comandos para identificar patrones de fallos
- Añada comandos de depuración específicos para verificar el entorno de ejecución
- Para scripts complejos, implemente registro detallado dentro del script mismo

```ini
[gcode_shell_command debug_env]
command: env | sort
timeout: 5.
verbose: True

[gcode_macro DEBUG_ENVIRONMENT]
gcode:
    RUN_SHELL_COMMAND CMD=debug_env
```

## Consideraciones de Seguridad Adicionales

- **No exponga comandos sensibles**: Evite configurar comandos que puedan comprometer la seguridad del sistema
- **Valide siempre la entrada del usuario**: Utilice patrones regex estrictos para los parámetros
- **Limite el acceso a recursos críticos**: Use variables de entorno para pasar información sensible en lugar de parámetros
- **Monitoree el uso**: Revise regularmente el historial de comandos para detectar actividades sospechosas
- **Actualice regularmente**: Mantenga actualizado el módulo para beneficiarse de mejoras de seguridad

## Recursos Adicionales

- [Documentación oficial de Klipper](https://www.klipper3d.org/)
- [Repositorio del creador original (Arksine)](https://github.com/Arksine)
- [Comunidad de Klipper en Discord](https://discord.klipper3d.org/)