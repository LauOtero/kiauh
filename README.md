Claro, aquí tienes el contenido convertido a formato Markdown sin HTML y traducido al español:

---

# Klipper Installation And Update Helper

Un script de instalación práctico que hace que instalar Klipper (y más) sea una tarea sencilla.

![KIAUH logo](https://raw.githubusercontent.com/dw-0/kiauh/master/resources/screenshots/kiauh.png)

## Licencia y estadísticas del proyecto

<p align="center">
  <a><img src="https://img.shields.io/github/license/dw-0/kiauh"></a>
  <a><img src="https://img.shields.io/github/stars/dw-0/kiauh"></a>
  <a><img src="https://img.shields.io/github/forks/dw-0/kiauh"></a>
  <a><img src="https://img.shields.io/github/languages/top/dw-0/kiauh?logo=gnubash&logoColor=white"></a>
  <a><img src="https://img.shields.io/github/v/tag/dw-0/kiauh"></a>
  <br />
  <a><img src="https://img.shields.io/github/last-commit/dw-0/kiauh"></a>
  <a><img src="https://img.shields.io/github/contributors/dw-0/kiauh"></a>
</p>

## Instrucciones

### Prerrequisitos

KIAUH es un script que te ayuda a instalar Klipper en un sistema operativo Linux que ya ha sido grabado en la tarjeta SD de tu Raspberry Pi (u otro SBC). Por lo tanto, debes asegurarte de tener un sistema Linux funcional. Se recomienda `Raspberry Pi OS Lite (ya sea 32 bits o 64 bits)` si estás usando un Raspberry Pi. El [Raspberry Pi Imager](https://www.raspberrypi.com/software/) es la forma más simple de grabar una imagen como esta en una tarjeta SD.

* Una vez que hayas descargado, instalado e iniciado el Raspberry Pi Imager, selecciona `Choose OS -> Raspberry Pi OS (other)`:

  ![Seleccionar OS](https://raw.githubusercontent.com/dw-0/kiauh/master/resources/screenshots/rpi_imager1.png)

* Luego selecciona `Raspberry Pi OS Lite (32 bit)` (o 64 bits si prefieres usarlo):

  ![Seleccionar Raspberry Pi OS Lite](https://raw.githubusercontent.com/dw-0/kiauh/master/resources/screenshots/rpi_imager2.png)

* Vuelve al menú principal del Raspberry Pi Imager y selecciona la tarjeta SD correspondiente a la que deseas grabar la imagen.
* Asegúrate de ir a las Opciones Avanzadas (el ícono de engranaje en la esquina inferior izquierda del menú principal) y habilitar SSH y configurar Wi-Fi.
* Si necesitas más ayuda para usar el Raspberry Pi Imager, consulta la [documentación oficial](https://www.raspberrypi.com/documentation/computers/getting-started.html).
* Estos pasos **solo** se aplican si estás utilizando un Raspberry Pi. Si deseas usar un SBC diferente (como una Orange Pi u otros derivados de Pi), busca cómo obtener una imagen Linux apropiada para grabar en la tarjeta SD antes de proceder (generalmente se hace con Balena Etcher en esos casos). También asegúrate de que KIAUH pueda funcionar y operar en la distribución Linux que vas a grabar. Tendrás más éxito con distribuciones basadas en Debian 11 Bullseye. Lee las notas más abajo en este documento.

### Descargar y usar KIAUH

**Advertencia: El uso de este script ocurre bajo tu propio riesgo.**

* **Paso 1:**  
Para descargar este script, es necesario tener instalado git. Si no tienes git instalado o si no estás seguro, ejecuta el siguiente comando:
  ```shell
  sudo apt-get update && sudo apt-get install git -y
  ```

* **Paso 2:**  
Una vez instalado git, usa el siguiente comando para descargar KIAUH en tu directorio home:
  ```shell
  cd ~ && git clone https://github.com/dw-0/kiauh.git
  ```

* **Paso 3:**  
Finalmente, inicia KIAUH ejecutando el siguiente comando:
  ```shell
  ./kiauh/kiauh.sh
  ```

* **Paso 4:**  
Ahora deberías encontrarte en el menú principal de KIAUH. Verás varias acciones para elegir dependiendo de lo que quieras hacer. Para elegir una acción, simplemente escribe el número correspondiente en el prompt "Perform action" y confirma presionando ENTER.

## Notas

- Se ha probado principalmente en Raspberry Pi OS Lite (Debian 10 Buster / Debian 11 Bullseye)
  - Otras distribuciones basadas en Debian (como Ubuntu 20 a 22) probablemente funcionarán también
  - Se reporta que funciona en Armbian también, pero no se ha probado en detalle
- Durante el uso de este script se te pedirá tu contraseña de sudo. Hay varias funciones involucradas que requieren privilegios de sudo.

## Fuentes y más información

| **Klipper** | **Moonraker** | **Mainsail** |
|-------------|---------------|--------------|
| ![Klipper Logo](https://raw.githubusercontent.com/Klipper3d/klipper/master/docs/img/klipper-logo.png) | ![Arksine avatar](https://avatars.githubusercontent.com/u/9563098?v=4) | ![Mainsail Logo](https://raw.githubusercontent.com/mainsail-crew/docs/master/assets/img/logo.png) |
| por [KevinOConnor](https://github.com/KevinOConnor) | por [Arksine](https://github.com/Arksine) | por [mainsail-crew](https://github.com/mainsail-crew) |

| **Fluidd** | **KlipperScreen** | **OctoPrint** |
|------------|-------------------|---------------|
| ![Fluidd Logo](https://raw.githubusercontent.com/fluidd-core/fluidd/master/docs/assets/images/logo.svg) | ![jordanruthe avatar](https://avatars.githubusercontent.com/u/31575189?v=4) | ![OctoPrint Logo](https://raw.githubusercontent.com/OctoPrint/OctoPrint/master/docs/images/octoprint-logo.png) |
| por [fluidd-core](https://github.com/fluidd-core) | por [jordanruthe](https://github.com/jordanruthe) | por [OctoPrint](https://github.com/OctoPrint) |

| **Moonraker-Telegram-Bot** | **PrettyGCode para Klipper** | **Obico para Klipper** |
|----------------------------|------------------------------|------------------------|
| ![nlef avatar](https://avatars.githubusercontent.com/u/52351624?v=4) | ![Kragrathea avatar](https://avatars.githubusercontent.com/u/5917231?v=4) | ![Obico logo](https://avatars.githubusercontent.com/u/46323662?s=200&v=4) |
| por [nlef](https://github.com/nlef) | por [Kragrathea](https://github.com/Kragrathea) | por [Obico](https://github.com/TheSpaghettiDetective) |

| **Mobileraker's Companion** | **OctoEverywhere para Klipper** | **OctoApp para Klipper** |
|-----------------------------|-------------------------------|--------------------------|
| ![Mobileraker Logo](https://raw.githubusercontent.com/Clon1998/mobileraker/master/assets/icon/mr_appicon.png) | ![OctoEverywhere Logo](https://octoeverywhere.com/img/logo.svg) | ![OctoApp Logo](https://octoapp.eu/octoapp.webp) |
| por [Patrick Schmidt](https://github.com/Clon1998) | por [Quinn Damerell](https://github.com/QuinnDamerell) | por [Christian Würthner](https://github.com/crysxd) |

| **Klipper-Backup** | **SimplyPrint para Klipper** |
|--------------------|----------------------------|
| ![Staubgeborener Avatar](https://avatars.githubusercontent.com/u/28908603?v=4) | ![SimplyPrint Avatar](https://avatars.githubusercontent.com/u/64896552?s=200&v=4) |
| por [Staubgeborener](https://github.com/Staubgeborener) | por [SimplyPrint](https://github.com/SimplyPrint) |

## Contribuidores

[![Contribuidores](https://contrib.rocks/image?repo=dw-0/kiauh)](https://github.com/dw-0/kiauh/graphs/contributors)

## Créditos

* Un gran gracias a [lixxbox](https://github.com/lixxbox) por ese increíble logotipo de KIAUH.
* También, un gran gracias a todos quienes apoyaron mi trabajo con [Ko-fi](https://ko-fi.com/dw__0).
* Y último pero no menos importante: ¡Gracias a todos los contribuidores y miembros de la comunidad de Klipper que les gusta y comparten este proyecto!

## Agradecimientos especiales

Un agradecimiento especial a JetBrains por patrocinar este proyecto con su increíble software.

[![JetBrains Logo](https://resources.jetbrains.com/storage/products/company/brand/logos/jb_beam.png)](https://www.jetbrains.com/community/opensource/#support)

---

Espero que esto te sea útil. Si necesitas algo más, no dudes en preguntar.