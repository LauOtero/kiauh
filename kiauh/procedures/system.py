# ======================================================================= #
#  Copyright (C) 2020 - 2025 Dominik Willner <th33xitus@gmail.com>        #
#                                                                         #
#  This file is part of KIAUH - Klipper Installation And Update Helper    #
#  https://github.com/dw-0/kiauh                                          #
#                                                                         #
#  This file may be distributed under the terms of the GNU GPLv3 license  #
# ======================================================================= #

from pathlib import Path
from subprocess import PIPE, CalledProcessError, run

from core.logger import DialogType, Logger
from utils.common import check_install_dependencies, get_current_date
from utils.fs_utils import check_file_exist
from utils.input_utils import get_confirm, get_string_input


def change_system_hostname() -> None:
    """
    Procedimiento para cambiar el nombre del sistema.
    :return:
    """

    Logger.print_dialog(
        DialogType.CUSTOM,
        [
            "Cambiar el nombre del sistema te permite acceder a una interfaz web "
            "instalada simplemente escribiendo el nombre del host así en el navegador:",
            "\n\n",
            "http://<hostname>.local",
            "\n\n",
            "Ejemplo: Si configuras el nombre del host como 'mi-impresora', puedes acceder a "
            "la interfaz web instalada escribiendo 'http://mi-impresora.local' en el "
            "navegador.",
        ],
        custom_title="CAMBIAR NOMBRE DEL SISTEMA",
    )
    if not get_confirm("¿Deseas cambiar el nombre del sistema?", default_choice=False):
        return

    Logger.print_dialog(
        DialogType.CUSTOM,
        [
            "Caracteres permitidos: a-z, 0-9 y '-'",
            "El nombre no debe contener lo siguiente:",
            "\n\n",
            "● Ningún carácter especial",
            "● Sin guiones al inicio o final",
        ],
    )
    hostname = get_string_input(
        "Ingresa el nuevo nombre del sistema",
        regex=r"^[a-z0-9]+([a-z0-9-]*[a-z0-9])?$",
    )
    if not get_confirm(f"¿Cambiar el nombre del sistema a '{hostname}'?", default_choice=False):
        Logger.print_info("Abortando cambio de nombre del sistema ...")
        return

    try:
        Logger.print_status("Cambiando nombre del sistema ...")

        Logger.print_status("Verificando dependencias ...")
        check_install_dependencies({"avahi-daemon"}, include_global=False)

        # create or backup hosts file
        Logger.print_status("Creando respaldo del archivo hosts ...")
        hosts_file = Path("/etc/hosts")
        if not check_file_exist(hosts_file, True):
            cmd = ["sudo", "touch", hosts_file.as_posix()]
            run(cmd, stderr=PIPE, check=True)
        else:
            date_time = get_current_date()
            name = f"hosts.{date_time.get('date')}-{date_time.get('time')}.bak"
            hosts_file_backup = Path(f"/etc/{name}")
            cmd = [
                "sudo",
                "cp",
                hosts_file.as_posix(),
                hosts_file_backup.as_posix(),
            ]
            run(cmd, stderr=PIPE, check=True)
        Logger.print_ok()

        # call hostnamectl set-hostname <hostname>
        Logger.print_status(f"Configurando nombre del sistema a '{hostname}' ...")
        cmd = ["sudo", "hostnamectl", "set-hostname", hostname]
        run(cmd, stderr=PIPE, check=True)
        Logger.print_ok()

        # add hostname to hosts file at the end of the file
        Logger.print_status("Escribiendo nuevo nombre del sistema en /etc/hosts ...")
        stdin = f"127.0.0.1       {hostname}\n"
        cmd = ["sudo", "tee", "-a", hosts_file.as_posix()]
        run(cmd, input=stdin.encode(), stderr=PIPE, stdout=PIPE, check=True)
        Logger.print_ok()

        Logger.print_ok("¡Nuevo nombre del sistema configurado exitosamente!")
        Logger.print_ok("¡Recuerda reiniciar para que los cambios surtan efecto!\n")

    except CalledProcessError as e:
        Logger.print_error(f"Error durante el procedimiento de cambio de nombre: {e}")
        return
