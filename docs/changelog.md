## Registro de cambios

Este documento cubre posibles cambios importantes en KIAUH.

### 2024-08-31 (v6.0.0-alpha.1)
¡Hace tiempo que no nos vemos, pero aquí estamos de nuevo!
Han pasado muchas cosas en segundo plano, pero ahora es momento de sacarlo a la luz.

#### ¡KIAUH ha alcanzado la versión 6! Bueno, al menos en estado alfa...

El proyecto ha visto una reescritura completa del script desde cero en Python.
Requiere Python 3.8 o más reciente para ejecutarse. Debido a que esta actualización aún está en estado alfa, pueden ocurrir errores.
Durante el inicio, se te preguntará si deseas iniciar la nueva versión 6 o la antigua versión 5.
Mientras la versión 6 esté en estado pre-lanzamiento, la versión 5 seguirá disponible. Si hay problemas críticos
con la nueva versión que se pasaron por alto, siempre puedes volver a la versión anterior.

En caso de que hayas seleccionado no preguntar sobre qué versión iniciar (opción 3 o 4 en el diálogo de inicio) y quieras
revertir esa decisión, encontrarás una línea llamada `version_to_launch=` dentro del archivo `.kiauh.ini` en tu directorio home.
Simplemente borra esa línea, guarda el archivo y reinicia KIAUH. KIAUH te preguntará nuevamente qué versión deseas iniciar.

Aquí hay una lista de los cambios más importantes en KIAUH con respecto a la versión 6:
- La mayoría de las características disponibles en KIAUH v5 siguen disponibles; solo se migraron de Bash a Python.
- Ahora es posible agregar nuevas/eliminar instancias a/de instalaciones multi-instancia existentes de Klipper y Moonraker
- KIAUH ahora tiene un Sistema de Extensiones. Esto permite a los contribuyentes agregar nuevos instaladores a KIAUH sin tener que modificar el script principal.
    - Ahora encontrarás algunas de las características que antes estaban disponibles en el Menú de Instalador en el Menú de Extensiones.
    - Las extensiones actuales son:
        - Comando Shell G-Code (anteriormente en el Menú Avanzado)
        - Instalador de Temas Mainsail (anteriormente en el Menú Avanzado)
        - Klipper-Backup (¡nuevo en v6!)
        - Bot de Telegram Moonraker (anteriormente en el Menú de Instalador)
        - PrettyGCode para Klipper (anteriormente en el Menú de Instalador)
        - Obico para Klipper (anteriormente en el Menú de Instalador)
    - Las siguientes extensiones adicionales están planeadas, pero aún no disponibles:
        - Spoolman (disponible en v5 en el Menú de Instalador)
        - OctoApp (disponible en v5 en el Menú de Instalador)
- KIAUH ahora tiene su propio archivo de configuración
    - El archivo tiene algunos valores predeterminados para las opciones actualmente soportadas
    - Podría haber más opciones en el futuro
    - Está ubicado en el directorio raíz de KIAUH y se llama `default.kiauh.cfg`
        - NO EDITES el archivo predeterminado directamente, en su lugar haz una copia y llámala `kiauh.cfg`
        - Los ajustes cambiados a través del Menú Avanzado se escribirán en el `kiauh.cfg`
- Se eliminó el soporte para OctoPrint

¡Siéntete libre de probar la versión 6 y reportar cualquier error o problema que encuentres! Se agradece cualquier comentario.

### 2023-06-17
¡KIAUH ha agregado soporte para instalar el complemento de Mobileraker!
Mobileraker es una aplicación gratuita y de código abierto para Android e iOS para Klipper, que utiliza la API de Moonraker, permitiéndote
controlar tu impresora. ¡Gracias a [Clon1998](https://github.com/Clon1998) por agregar esta función!

### 2023-02-03
El instalador de MJPG-Streamer fue reemplazado por crowsnest. Es un servicio de webcam mejorado que utiliza ustreamer.
Por favor mira aquí para información adicional sobre crowsnest y cómo configurarlo: https://github.com/mainsail-crew/crowsnest \
No está claro si el instalador anterior de MJPG-Streamer será actualizado y volverá a KIAUH.
Muchas gracias a [KwadFan](https://github.com/KwadFan) por escribir la implementación de crowsnest.

### 2022-10-31
Algunas funciones se actualizaron, aunque no todas.

Las siguientes funciones no están disponibles actualmente:
- Instalación de: MJPG-Streamer
- Todas las funciones de respaldo y la Carga de Registros

### 2022-10-20
¡KIAUH ha alcanzado la versión principal 5!

Recientemente Moonraker introdujo algunos cambios que hacen necesario cambiar la estructura de carpetas de las configuraciones de impresora.
Si estás interesado en los detalles, revisa este PR: https://github.com/Arksine/moonraker/pull/491 \
Aunque Moonraker tiene algunos mecanismos disponibles para migrar configuraciones existentes a la nueva estructura de archivos con el uso de enlaces simbólicos, se recomienda
realizar instalaciones nuevas y limpias.

¡El salto de versión de KIAUH a v5 es un cambio importante debido a estos cambios mayores! ¡Esto significa que v4 y v5 no son compatibles entre sí!
Esta es también la razón por la que actualmente serás recibido por una notificación amarilla en el menú principal de KIAUH que lleva a este registro de cambios.
Decidí deshabilitar algunas funciones del script y concentrarme en lanzar los cambios requeridos a los componentes principales de este script.
Trabajaré en actualizar las otras partes del script pieza por pieza durante los próximos días/semanas.
Así que me disculpo de antemano si alguno de los componentes que querías instalar o usar temporalmente no puede ser instalado o usado en este momento.

Las siguientes funciones no están disponibles actualmente:
- Instalación de: KlipperScreen, Obico, Octoprint, MJPG-Streamer, Bot de Telegram y PrettyGCode
- Todas las funciones de respaldo y la Carga de Registros

**¿Entonces qué está funcionando?**\
Instalación de Klipper, Moonraker, Mainsail y Fluidd. ¡Tanto configuraciones individuales como multi-instancia funcionan!\
Como ya se dijo, el resto vendrá en un futuro cercano. La actualización y eliminación de componentes ya instalados debería seguir funcionando.

**¿Qué se eliminó?**\
Se eliminó la opción de cambiar el directorio de configuración de Klipper. De ahora en adelante no será posible cambiar
el directorio de configuración desde KIAUH y se impone la nueva estructura de archivos.

**¿Qué pasa si no tengo una instalación existente de Klipper/Moonraker en este momento?**\
Nada importante en qué pensar, instala Klipper y Moonraker. KIAUH instalará ambos con la nueva estructura de archivos.

**¿Qué pasa si tengo una instalación existente de Klipper/Moonraker?**\
Primero que nada: ¡Respaldos! Por favor copia todos tus archivos de configuración y la base de datos de Moonraker (es una carpeta oculta, usualmente `~/.moonraker_database`) a una ubicación segura.
Después de eso, desinstala Klipper y Moonraker con KIAUH. Luego puedes proceder y reinstalar ambos con KIAUH nuevamente. Es importante que estés en KIAUH v5 para eso!
Una vez que todo esté instalado nuevamente, necesitas copiar manualmente tus archivos de configuración desde la antigua carpeta `~/klipper_config` a la nueva `~/printer_data/config`.
Los enlaces simbólicos anteriores creados por Moonraker a carpetas de la antigua estructura de archivos ya no funcionarán, ¡necesitas mover los archivos a su nueva ubicación ahora!
Haz lo mismo con los dos archivos dentro de `~/.moonraker_database`. Mueve/copia los archivos a `~/printer_data/database`. Si `~/printer_data/database` ya está poblada con un `data.mdb` y `lock.mdb`
bórralos o simplemente sobrescríbelos. No se debería perder nada ya que deberían ser archivos de base de datos vacíos. De todos modos, hiciste respaldos, ¿verdad?
Ahora puedes proceder y reiniciar Moonraker. Ya sea desde Mainsail o Fluidd, o usa SSH y ejecuta `sudo systemctl restart moonraker`.
Si todo salió bien, deberías estar listo para continuar. Si ves algunas advertencias de Moonraker sobre opciones obsoletas en el `moonraker.conf`, procede a resolverlas.
No las cubriré en detalle aquí. Una buena fuente es la documentación de Moonraker: https://moonraker.readthedocs.io/en/latest/configuration/
**¿Qué pasa si tengo una instalación multi-instancia existente de Klipper/Moonraker?**\
Básicamente se aplican los mismos pasos que se requieren para instalaciones de una sola instancia a las configuraciones multi-instancia. Así que por favor lee el párrafo anterior si aún no lo has hecho.
Primero haz respaldos de todo. Luego elimina e instala nuevamente la cantidad deseada de instancias de Klipper y Moonraker.
Ahora necesitas mover todos los archivos de configuración y base de datos a sus nuevas ubicaciones.\
Ejemplo con una instancia llamada `printer_1`:\
Los archivos de configuración van de `~/klipper_config/printer_1` a `~/printer_1_data/config`.
Los archivos de base de datos van de `~/.moonraker_database_1` a `~/printer_1_data/database`.
Ahora reinicia todos los servicios de Moonraker. Puedes reiniciarlos todos a la vez si inicias KIAUH, y en el menú principal escribes `restart moonraker` y presionas Enter.

Espero haber cubierto las cosas más importantes. En caso de que necesites más ayuda, el Discord oficial de Klipper es un buen lugar para pedir ayuda.

### 2022-08-15
¡Se agregó soporte para "Obico for Klipper"! ¡Muchas gracias a [kennethjiang](https://github.com/kennethjiang) por ayudarme con la implementación!

### 2022-05-29
¡KIAUH ha alcanzado la versión principal 4!
* característica: Klipper puede instalarse bajo Python3 (aún considerado experimental)
* característica: Klipper puede instalarse desde repositorios personalizados / forks no oficiales
* característica: Nombre de instancia personalizado para instalaciones multi-instancia de Klipper
  * Cualquier otra multi-instancia compartirá el mismo nombre dado a la instancia correspondiente de Klipper
  * Por ejemplo: klipper-voron2 -> moonraker-voron2 -> moonraker-telegram-bot-voron2
* característica: Opción para permitir la instalación/actualización a versiones inestables de Mainsail y Fluidd
  * por defecto solo se instalan/actualizan versiones estables
* característica: Las instalaciones multi-instancia de OctoPrint ahora tienen cada una su propio entorno virtual de python
  * permite la instalación independiente de plugins para cada instancia
* característica: Implementación del uso de shellcheck durante el desarrollo
* característica: Implementación de un mecanismo simple de registro
* característica: La función de carga de registros ahora también permite cargar otros archivos de registro (kiauh.log, webcamd.log etc.)
* característica: se agregaron varios nuevos diálogos de ayuda que intentan explicar varias funciones
* corrección: Durante la instalación de Klipper, se realizan verificaciones de membresía de grupo para `tty` y `dialout`
* refactorización: rediseño del menú de configuración para un mejor control de las nuevas características de KIAUH
* refactorización: Se eliminó el soporte para DWC y DWC-for-Klipper
* refactorización: La configuración de respaldo antes de actualizar se movió al menú de configuración de KIAUH
* refactorización: Se eliminó la función de cambiar rama (fue reemplazada por la característica de repositorio personalizado de Klipper)
* refactorización: Se eliminaron las secciones del administrador de actualizaciones para Mainsail, Fluidd y KlipperScreen de la plantilla moonraker.conf
  * Ahora se agregarán individualmente durante la instalación de la interfaz correspondiente
* refactorización: La función de reversión fue rediseñada y ahora también permite reversiones de Moonraker
  * Ahora toma entradas numéricas y revierte el repositorio correspondiente por la cantidad dada
  * KIAUH ya no guarda estados anteriores en su configuración como lo hacía con el enfoque anterior

### 2022-01-29
* A partir del 28 de enero, Moonraker puede hacer uso de PackageKit y PolicyKit.\
Más detalles se pueden encontrar [aquí](
https://github.com/Arksine/moonraker/issues/349) y [aquí](https://github.com/Arksine/moonraker/pull/346)
* KIAUH instalará las reglas de PolicyKit de Moonraker por defecto al __instalar__ Moonraker
* KIAUH también instalará las reglas de PolicyKit de Moonraker al __actualizar__ Moonraker __vía KIAUH__ a partir de ahora

### 2021-12-30
* Se actualizó la documentación para el uso de la [Extensión de Comandos Shell G-Code](docs/gcode_shell_command.md)
* Se hizo evidente que faltan algunos grupos de usuarios en algunos sistemas. Una membresía faltante del grupo video \
por ejemplo causó problemas al instalar mjpg-streamer mientras no se usaba el usuario pi predeterminado. \
Otros problemas podrían ocurrir al intentar flashear un MCU en distribuciones Debian o Ubuntu donde un usuario podría no ser parte
del grupo dialout por defecto. También se realiza una verificación del grupo tty. El grupo tty es necesario para configurar
un MCU linux (actualmente no soportado por KIAUH).
* Hay un problema al intentar instalar Mainsail o Fluidd en Ubuntu 21.10. Los permisos en esa distribución parecen haber visto una reorganización
 en comparación con 20.04 y los usuarios serán recibidos con un mensaje "Error 403 - Permiso denegado" después de instalar una de las interfaces web de Klipper.
Todavía tengo que encontrar una solución viable para eso.

### 2021-09-28
* ¡Nueva Característica! Se agregó un instalador para el Bot de Telegram para Moonraker por [nlef](https://github.com/nlef).
¡Revisa su proyecto! Recuerda reportar todos los problemas y/o errores relacionados con ese proyecto en su repositorio correspondiente y no aquí 😛.\
Puedes encontrarlo aquí: https://github.com/nlef/moonraker-telegram-bot

### 2021-09-24
* La función de flasheo se ajustó un poco. Ahora es posible flashear controladores que están conectados por UART y por lo tanto accesibles vía `/dev/ttyAMA0`. Ahora tienes que seleccionar un método de conexión antes de flashear que puede ser USB o UART.
* Debido a varias solicitudes a lo largo del tiempo, ahora he creado una cuenta Ko-fi para aquellos que quieran apoyar este proyecto y mi trabajo con una pequeña donación. Muchas gracias por adelantado a todos los futuros donantes. Puedes apoyarme en Ko-fi con este enlace: https://ko-fi.com/th33xitus
* Como siempre, si encuentras algún error o problema por favor repórtalo. Probé el pequeño rediseño que hice con el hardware que tengo disponible y no he encontrado ningún mal funcionamiento al flashearlos todavía.

### 2021-08-10
* ¡KIAUH ahora soporta la instalación del Visor de GCode "PrettyGCode for Klipper" creado por [Kragrathea](https://github.com/Kragrathea)! La instalación, actualización y eliminación son posibles con KIAUH. Para más detalles sobre este genial software, por favor mira aquí: https://github.com/Kragrathea/pgcode

### 2021-07-10
* Los archivos de configuración de NGINX se actualizaron para estar sincronizados con MainsailOS y FluiddPi. Los problemas con el servicio NGINX que no iniciaba debido a una configuración incorrecta deberían estar resueltos ahora. Para obtener los archivos de configuración actualizados, por favor elimina Moonraker y Mainsail / Fluidd con KIAUH primero y luego reinstálalos. Una verificación automatizada de archivos para esos archivos de configuración podría seguir en el futuro que entonces automatiza la actualización de esos archivos si hubiera cambios importantes.

* El `moonraker.conf` predeterminado se actualizó para reflejar los cambios recientes en la sección del administrador de actualizaciones. El canal de actualización está configurado en `dev`.

### 2021-06-29
* KIAUH ahora parcheará el nuevo `log_path` a los archivos moonraker.conf existentes al actualizar Moonraker y cuando falte la entrada. Antes de eso, era necesario que el usuario proporcionara esa ruta manualmente para hacer que Fluidd mostrara los archivos de registro en su interfaz. Este problema debería estar resuelto ahora.

### 2021-06-15

* Moonraker introdujo un `log_path` opcional que los clientes pueden usar para mostrar archivos de registro ubicados en esa carpeta a sus usuarios. Más información aquí: https://github.com/Arksine/moonraker/commit/829b3a4ee80579af35dd64a37ccc092a1f67682a \
Los desarrolladores de clientes acordaron usar `~/klipper_logs` como la nueva ruta de registro predeterminada.\
Esto significa que, a partir de ahora, los servicios de Klipper y Moonraker instalados con KIAUH colocarán sus archivos de registro en esa carpeta mencionada.
* Además, KIAUH ahora detectará servicios systemd de Klipper y Moonraker que todavía usan la ubicación predeterminada antigua de `/tmp/<service>.log` y los actualizará la próxima vez que el usuario actualice Klipper y/o Moonraker con la función de actualización de KIAUH.
* Se crearán enlaces simbólicos adicionales para los siguientes archivos de registro junto con esos procedimientos de actualización para hacerlos accesibles a través de la interfaz web una vez que sea compatible:
    - webcamd.log
    - mainsail-access.log
    - mainsail-error.log
    - fluidd-access.log
    - fluidd-error.log
* Para usuarios de MainsailOS y FluiddPi:\
MainsailOS y FluiddPi cambiarán el servicio Klipper incluido de SysVinit a systemd probablemente con su próximo lanzamiento. KIAUH ya puede ayudar a migrar versiones antiguas de MainsailOS (0.4.0 y anteriores) y FluiddPi (v1.13.0) para que coincidan con su nueva estructura de servicios, archivos y carpetas para que no tengas que volver a flashear la tarjeta SD de tu Raspberry Pi.\
En detalle, esto es lo que va a suceder cuando uses el nuevo "Asistente de Migración CustomPiOS" desde el Menú Avanzado\
`(Menú Principal -> 4 -> Enter -> 10 -> Enter)` en un breve resumen:
    * El servicio SysVinit de Klipper será reemplazado por un servicio systemd de Klipper
    * Klipper y Moonraker usarán el nuevo directorio de registros `~/klipper_logs`
    * El servicio webcamd se actualiza
    * El script webcamd se actualiza y se mueve de `/root/bin/webcamd` a `/usr/local/bin/webcamd`
    * El `upstreams.conf` de NGINX se actualiza para poder configurar hasta 4 webcams
    * El `mainsail.txt` / `fluiddpi.txt` se mueve de `/boot` a `~/klipper_config` y se renombra a `webcam.txt`
    * Se crean enlaces simbólicos para webcamd.log y varios registros de NGINX en `~/klipper_config`
    * Se agregan archivos de configuración para Klipper, Moonraker y webcamd a `/etc/logrotate.d`
    * Si todavía existen, se eliminarán dos líneas de las configuraciones de macros mainsail.cfg o client_macros.cfg:\
    `SAVE_GCODE_STATE NAME=PAUSE_state` y `RESTORE_GCODE_STATE NAME=PAUSE_state`
* **Por favor nota:**\
El "Asistente de Migración CustomPiOS" está destinado a funcionar solo en sistemas MainsailOS y FluiddPi "vanilla". No intentes migrar un sistema MainsailOS o FluiddPi modificado (por ejemplo, si ya usaste KIAUH para reinstalar servicios o configurar una instalación multi-instancia para Klipper / Moonraker). Esto no funcionará.

### 2021-01-31

* **Este es uno grande... KIAUH v3.0 está aquí.**\
Con esta actualización ahora puedes instalar múltiples instancias de Klipper, Moonraker, Duet Web Control u Octoprint en la misma Pi. Esta fue una gran reescritura de todo el script. Así que pueden aparecer errores pero con la ayuda de algunos probadores, creo que no debería haber ninguno crítico. En este sentido gracias a @lixxbox y @zellneralex por las pruebas.

* Cambios importantes en cómo se configuran las instalaciones ahora: Todos los componentes se instalan como servicios systemd. ¡La instalación vía init.d se eliminó por completo! Esto no debería afectarte en absoluto, ya que las distribuciones linux comunes como RaspberryPi OS o distribuciones personalizadas como MainsailOS, FluiddPi u OctoPi soportan ambas formas de instalar servicios. Solo quería mencionarlo aquí.

* Ahora con KIAUH v3.0 y capacidades de instalación multi-instancia, hay algunas cosas que señalar. Ahora necesitarás decirle a KIAUH dónde están ubicadas las configuraciones de tu impresora cuando instales Klipper por primera vez. Aunque no se recomienda, puedes cambiar esta ubicación con la ayuda de KIAUH y reescribir Klipper y Moonraker para usar la nueva ubicación.

* Al configurar un sistema multi-instancia, la estructura de carpetas solo cambiará ligeramente. El objetivo era mantenerlo lo más compatible posible con las distribuciones personalizadas como mainsailOS y FluiddPi. Esto debería ayudar a convertir una configuración de una sola instancia de mainsailOS/FluiddPi a una configuración multi-instancia en poco tiempo, pero manteniendo la compatibilidad hacia atrás de una sola instancia si es necesario en un momento posterior.

* La estructura de carpetas es la siguiente al configurar multi-instancias:\
Cada instancia de impresora obtendrá su propia carpeta dentro de tu ubicación de configuración. La decisión de esta estructura específica se tomó para hacer la conversión a una configuración multi-instancia lo más indolora y fácil posible.
Aquí hay un ejemplo:
    ```shell
    /home/<username>
              └── klipper_config
                  ├── printer_1
                  │   ├── printer.cfg
                  │   └── moonraker.conf
                  ├── printer_2
                  │   ├── printer.cfg
                  │   └── moonraker.conf
                  └── printer_n
                      ├── printer.cfg
                      └── moonraker.conf
    ```
* También al configurar múltiples instancias de cada servicio, el nombre de cada servicio cambia ligeramente.
Cada servicio obtiene su instancia correspondiente agregada al nombre del archivo de servicio.

    **¡Esto solo aplica a múltiples instancias! ¡Las instalaciones de una sola instancia con KIAUH mantendrán sus nombres originales!**

    Correspondiendo al ejemplo del árbol de archivos anterior, esto significaría:
    ```
    Servicios Klipper:
            --> klipper-1.service
            --> klipper-2.service
            --> klipper-n.service

    Servicios Moonraker:
            --> moonraker-1.service
            --> moonraker-2.service
            --> moonraker-n.service
    ```
* Las mismas reglas de archivos de servicio mencionadas arriba aplican a OctoPrint aunque solo Klipper y Moonraker se muestran en este ejemplo.

* Puedes iniciar, detener y reiniciar todas las instancias de Klipper, Moonraker y OctoPrint desde el menú principal de KIAUH. Para hacer esto, simplemente escribe "stop klipper", "start moonraker", "restart octoprint" y así sucesivamente.

* KIAUH v3.0 reubicó su archivo ini. Ahora es un archivo oculto en el directorio home del usuario llamado `.kiauh.ini`. Esto tiene el beneficio de mantener todos los valores en ese archivo entre posibles reinstalaciones de KIAUH. De otro modo ese archivo se perdería.

* Se eliminó la opción de agregar más clientes confiables al archivo moonraker.conf. Ya que puedes editar este archivo directamente dentro de Mainsail o Fluidd, solo se hacen algunas entradas básicas que te permiten funcionar.

* Apuesto a que me he olvidado de mencionar otras cosas también porque me tomó bastante tiempo reescribir muchas funciones. ¡Así que solo espero que te guste la nueva versión! 😄

### 2020-11-28

* ¡KIAUH ahora soporta la instalación, actualización y eliminación de [KlipperScreen](https://github.com/jordanruthe/KlipperScreen)! ¡Esta característica fue proporcionada por [jordanruthe](https://github.com/jordanruthe)! ¡Gracias!

### 2020-11-18

* Algunos cambios en Fluidd causaron una pequeña modificación en cómo KIAUH instalará/actualizará Fluidd de ahora en adelante. Por favor revisa las [notas de lanzamiento de fluidd v1.0.0-rc0](https://github.com/cadriel/fluidd/releases/tag/v1.0.0-rc.0) para más información sobre qué modificaciones exactamente tuvieron que hacerse al archivo moonraker.conf. En resumen, KIAUH ahora siempre agregará las entradas requeridas al moonraker.conf si no están ya presentes.

### 2020-10-30:

* El usuario ahora puede elegir instalar Klipper como un servicio systemd.

* La extensión Shell Command y `shell_command.py` fueron renombrados a extensión G-Code Shell Command y `gcode_shell_command.py`. En caso de que el [PR pendiente](https://github.com/KevinOConnor/klipper/pull/2173) sea fusionado en el futuro, este fue un intento temprano de evitar posibles incompatibilidades. La [documentación de G-Code Shell Command](gcode_shell_command.md) ha sido actualizada en consecuencia.

* La forma en que KIAUH interactúa y escribe en el printer.cfg del usuario ha cambiado. Usualmente KIAUH escribía todo directamente en el printer.cfg. La forma en que funcionará de ahora en adelante es que se creará un nuevo archivo llamado `kiauh.cfg` si hay algo que necesita ser escrito en el printer.cfg y todo se escribirá en `kiauh.cfg` en su lugar. Lo único que entonces se escribe en el printer.cfg del usuario es `[include kiauh.cfg]`. Esta línea estará ubicada en la parte superior del printer.cfg existente con un pequeño comentario como nota. El usuario puede entonces decidir mantener el `kiauh.cfg` o tomar su contenido, colocarlo directamente en el printer.cfg y eliminar el `[include kiauh.cfg]`.

* El `mainsail_macros.cfg` fue renombrado a `webui_macros.cfg`. Ya que tanto Mainsail como Fluidd usan el mismo tipo de macros de pausa, cancelación y reanudación, se eligió un nombre más genérico para el archivo que contiene las macros de ejemplo que uno puede elegir instalar al instalar esas interfaces web.

### 2020-10-10:

* Se eliminó el soporte para cambiar la rama de Klipper a la rama moonraker-dev de @Arksine. El soporte para Moonraker se ha fusionado en la línea principal de Klipper hace mucho tiempo.

* Una nueva función está disponible desde el menú principal. Ahora puedes subir tus archivos de registro a http://paste.c-net.org/ para compartirlos con fines de depuración.

### 2020-10-06:

* Fluidd, una nueva interfaz de Klipper se agregó a la lista de instaladores disponibles. Al mismo tiempo algunas rutinas de instalación han cambiado o han visto alguna modificación. Se hicieron cambios en la instalación de configuraciones NGINX. Se introdujo un método para cambiar el puerto de escucha de una configuración de interfaz web si ya hay otra interfaz web escuchando en el puerto predeterminado (80).

* Por el momento, el instalador de Moonraker ya no pregunta si deseas instalar también una interfaz web. Por ahora, por lo tanto, debes instalarlas con sus respectivos instaladores. Por favor reporta cualquier error o problema que encuentres.

### 2020-09-17:

* La rama dev-2.0 será abandonada a partir de hoy. Si hiciste un checkout a esa rama en el pasado, debes hacer checkout de vuelta a master para recibir actualizaciones.

### 2020-09-12:

* ¡El antiguo [dwc2-for-klipper](https://github.com/Stephan3/dwc2-for-klipper) ya no será soportado!\
Hay un nuevo proyecto completamente reescrito disponible: [dwc2-for-klipper-socket](https://github.com/Stephan3/dwc2-for-klipper-socket).\
El instalador de este script también fue reescrito para hacer uso de ese nuevo proyecto. Ya no podrás instalar o eliminar el antiguo [dwc2-for-klipper](https://github.com/Stephan3/dwc2-for-klipper) con KIAUH si actualizaste KIAUH a la versión más reciente.
