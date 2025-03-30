# ======================================================================= #
#  Copyright (C) 2020 - 2025 Dominik Willner <th33xitus@gmail.com>        #
#                                                                         #
#  Este archivo es parte de KIAUH - Klipper Installation And Update Helper #
#  https://github.com/dw-0/kiauh                                          #
#                                                                         #
#  Este archivo puede distribuirse bajo los términos de la licencia GNU GPLv3 #
# ======================================================================= #
from __future__ import annotations

import os
import re
import select
import shutil
import socket
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from subprocess import DEVNULL, PIPE, CalledProcessError, Popen, check_output, run
from typing import List, Literal, Set, Tuple

from core.constants import SYSTEMD
from core.logger import Logger
from utils.fs_utils import check_file_exist, remove_with_sudo
from utils.input_utils import get_confirm

SysCtlServiceAction = Literal[
    "start",
    "stop",
    "restart",
    "reload",
    "enable",
    "disable",
    "mask",
    "unmask",
]
SysCtlManageAction = Literal["daemon-reload", "reset-failed"]


class VenvCreationFailedException(Exception):
    pass


def kill(opt_err_msg: str = "") -> None:
    """
    Termina la aplicación |
    :param opt_err_msg: un mensaje de error adicional opcional
    :return: None
    """

    if opt_err_msg:
        Logger.print_error(opt_err_msg)
    Logger.print_error("Ocurrió un error crítico. KIAUH fue terminado.")
    sys.exit(1)


def check_python_version(major: int, minor: int) -> bool:
    """
    Verifica la versión de Python y devuelve True si es al menos la versión dada
    :param major: la versión mayor a verificar
    :param minor: la versión menor a verificar
    :return: bool
    """
    if not (sys.version_info.major >= major and sys.version_info.minor >= minor):
        Logger.print_error("La verificación de la versión falló!")
        Logger.print_error(f"Se requiere Python {major}.{minor} o superior.")
        return False
    return True


def parse_packages_from_file(source_file: Path) -> List[str]:
    """
    Lee los nombres de los paquetes desde scripts bash, cuando están definidos como:
    PKGLIST="package1 package2 package3" |
    :param source_file: ruta del archivo fuente del que leer
    :return: Una lista de nombres de paquetes
    """

    packages = []
    with open(source_file, "r") as file:
        for line in file:
            line = line.strip()
            if line.startswith("PKGLIST="):
                line = line.replace('"', "")
                line = line.replace("PKGLIST=", "")
                line = line.replace("${PKGLIST}", "")
                packages.extend(line.split())

    return packages


def create_python_venv(
    target: Path,
    force: bool = False,
    allow_access_to_system_site_packages: bool = False,
) -> bool:
    """
    Crea un entorno virtual de Python 3 en el destino proporcionado.
    Devuelve True si el entorno virtual se creó con éxito.
    Devuelve False si el entorno virtual ya existe, la recreación fue declinada o la creación falló.
    :param target: Ruta donde crear el entorno virtual
    :param force: Forzar la recreación del entorno virtual
    :param allow_access_to_system_site_packages: dar al entorno virtual acceso al directorio de site-packages del sistema
    :return: bool
    """
    Logger.print_status("Configurando entorno virtual de Python ...")
    cmd = ["virtualenv", "-p", "/usr/bin/python3", target.as_posix()]
    cmd.append(
        "--system-site-packages"
    ) if allow_access_to_system_site_packages else None
    if not target.exists():
        try:
            run(cmd, check=True)
            Logger.print_ok("Configuración del entorno virtual exitosa!")
            return True
        except CalledProcessError as e:
            Logger.print_error(f"Error configurando el entorno virtual:\n{e}")
            return False
    else:
        if not force and not get_confirm(
            "El entorno virtual ya existe. ¿Recrear?", default_choice=False
        ):
            Logger.print_info("Saltando la recreación del entorno virtual ...")
            return False

        try:
            shutil.rmtree(target)
            create_python_venv(target)
            return True
        except OSError as e:
            log = f"Error eliminando el entorno virtual existente: {e.strerror}"
            Logger.print_error(log, False)
            return False
def update_python_pip(target: Path) -> None:
    """
    Actualiza pip en el destino proporcionado |
    :param target: Ruta del entorno virtual
    :return: None
    """
    Logger.print_status("Actualizando pip ...")
    try:
        pip_location: Path = target.joinpath("bin/pip")
        pip_exists: bool = check_file_exist(pip_location)

        if not pip_exists:
            raise FileNotFoundError("Error actualizando pip! No encontrado.")

        command = [pip_location.as_posix(), "install", "-U", "pip"]
        result = run(command, stderr=PIPE, text=True)
        if result.returncode != 0 or result.stderr:
            Logger.print_error(f"{result.stderr}", False)
            Logger.print_error("La actualización de pip falló!")
            return

        Logger.print_ok("Actualización de pip exitosa!")
    except FileNotFoundError as e:
        Logger.print_error(e)
        raise
    except CalledProcessError as e:
        Logger.print_error(f"Error actualizando pip:\n{e.output.decode()}")
        raise


def install_python_requirements(target: Path, requirements: Path) -> None:
    """
    Instala los paquetes de Python basados en un archivo requirements.txt proporcionado |
    :param target: Ruta del entorno virtual
    :param requirements: Ruta al archivo requirements.txt
    :return: None
    """
    try:
        # siempre actualiza pip antes de instalar los requisitos
        update_python_pip(target)

        Logger.print_status("Instalando requisitos de Python ...")
        command = [
            target.joinpath("bin/pip").as_posix(),
            "install",
            "-r",
            f"{requirements}",
        ]
        result = run(command, stderr=PIPE, text=True)

        if result.returncode != 0 or result.stderr:
            Logger.print_error(f"{result.stderr}", False)
            raise VenvCreationFailedException("La instalación de los requisitos de Python falló!")

        Logger.print_ok("Instalación de requisitos de Python exitosa!")

    except Exception as e:
        log = f"Error instalando requisitos de Python: {e}"
        Logger.print_error(log)
        raise VenvCreationFailedException(log)


def install_python_packages(target: Path, packages: List[str]) -> None:
    """
    Instala los paquetes de Python basados en una lista de paquetes proporcionada |
    :param target: Ruta del entorno virtual
    :param packages: lista de cadenas de paquetes requeridos
    :return: None
    """
    try:
        # siempre actualiza pip antes de instalar los requisitos
        update_python_pip(target)

        Logger.print_status("Instalando requisitos de Python ...")
        command = [
            target.joinpath("bin/pip").as_posix(),
            "install",
        ]
        for pkg in packages:
            command.append(pkg)
        result = run(command, stderr=PIPE, text=True)

        if result.returncode != 0 or result.stderr:
            Logger.print_error(f"{result.stderr}", False)
            raise VenvCreationFailedException("La instalación de los requisitos de Python falló!")

        Logger.print_ok("Instalación de requisitos de Python exitosa!")

    except Exception as e:
        log = f"Error instalando requisitos de Python: {e}"
        Logger.print_error(log)
        raise VenvCreationFailedException(log)


def update_system_package_lists(silent: bool, rls_info_change=False) -> None:
    """
    Actualiza la lista de paquetes del sistema |
    :param silent: Registrar información en la consola o no
    :param rls_info_change: Bandera para "--allow-releaseinfo-change"
    :return: None
    """
    cache_mtime: float = 0
    cache_files: List[Path] = [
        Path("/var/lib/apt/periodic/update-success-stamp"),
        Path("/var/lib/apt/lists"),
    ]
    for cache_file in cache_files:
        if cache_file.exists():
            cache_mtime = max(cache_mtime, os.path.getmtime(cache_file))

    update_age = int(time.time() - cache_mtime)
    update_interval = 6 * 3600  # 48 horas

    if update_age <= update_interval:
        return

    if not silent:
        Logger.print_status("Actualizando lista de paquetes...")

    try:
        command = ["sudo", "apt-get", "update"]
        if rls_info_change:
            command.append("--allow-releaseinfo-change")

        result = run(command, stderr=PIPE, text=True)
        if result.returncode != 0 or result.stderr:
            Logger.print_error(f"{result.stderr}", False)
            Logger.print_error("La actualización de la lista de paquetes del sistema falló!")
            return

        Logger.print_ok("Actualización de la lista de paquetes del sistema exitosa!")
    except CalledProcessError as e:
        Logger.print_error(f"Error actualizando la lista de paquetes del sistema:\n{e.stderr.decode()}")
        raise
def get_upgradable_packages() -> List[str]:
    """
    Lee todos los paquetes del sistema que pueden ser actualizados.
    :return: Una lista de nombres de paquetes disponibles para actualizar
    """
    try:
        command = ["apt", "list", "--upgradable"]
        output: str = check_output(command, stderr=DEVNULL, text=True, encoding="utf-8")
        pkglist = []
        for line in output.split("\n"):
            if "/" not in line:
                continue
            pkg = line.split("/")[0]
            pkglist.append(pkg)
        return pkglist
    except CalledProcessError as e:
        raise Exception(f"Error leyendo paquetes actualizables: {e}")


def check_package_install(packages: Set[str]) -> List[str]:
    """
    Verifica el sistema para paquetes instalados |
    :param packages: Lista de cadenas de nombres de paquetes
    :return: Una lista que contiene los nombres de paquetes que no están instalados
    """
    not_installed = []
    for package in packages:
        command = ["dpkg-query", "-f'${Status}'", "--show", package]
        result = run(
            command,
            stdout=PIPE,
            stderr=DEVNULL,
            text=True,
        )
        if "installed" not in result.stdout.strip("'").split():
            not_installed.append(package)

    return not_installed


def install_system_packages(packages: List[str]) -> None:
    """
    Instala una lista de paquetes del sistema |
    :param packages: Lista de nombres de paquetes del sistema
    :return: None
    """
    try:
        command = ["sudo", "apt-get", "install", "-y"]
        for pkg in packages:
            command.append(pkg)
        run(command, stderr=PIPE, check=True)

        Logger.print_ok("Paquetes instalados con éxito.")
    except CalledProcessError as e:
        Logger.print_error(f"Error instalando paquetes:\n{e.stderr.decode()}")
        raise


def upgrade_system_packages(packages: List[str]) -> None:
    """
    Actualiza una lista de paquetes del sistema |
    :param packages: Lista de nombres de paquetes del sistema
    :return: None
    """
    try:
        command = ["sudo", "apt-get", "upgrade", "-y"]
        for pkg in packages:
            command.append(pkg)
        run(command, stderr=PIPE, check=True)

        Logger.print_ok("Paquetes actualizados con éxito.")
    except CalledProcessError as e:
        raise Exception(f"Error actualizando paquetes:\n{e.stderr.decode()}")


# esto se siente algo hacky y no muy correcto, pero por ahora funciona
# ver: https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
def get_ipv4_addr() -> str:
    """
    Función auxiliar que devuelve la dirección IPv4 de la máquina actual
    abriendo un socket y enviando un paquete a una IP arbitraria. |
    :return: Dirección IPv4 local de la máquina actual
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # no necesita ser alcanzable
        s.connect(("192.255.255.255", 1))
        return str(s.getsockname()[0])
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def download_file(url: str, target: Path, show_progress=True) -> None:
    """
    Método auxiliar para descargar archivos desde una URL proporcionada |
    :param url: la URL del archivo
    :param target: la ruta objetivo incluyendo el nombre del archivo
    :param show_progress: mostrar progreso de descarga o no
    :return: None
    """
    try:
        if show_progress:
            urllib.request.urlretrieve(url, target, download_progress)
            sys.stdout.write("\n")
        else:
            urllib.request.urlretrieve(url, target)
    except urllib.error.HTTPError as e:
        Logger.print_error(f"Descarga fallida! Ocurrió un error HTTP: {e}")
        raise
    except urllib.error.URLError as e:
        Logger.print_error(f"Descarga fallida! Ocurrió un error de URL: {e}")
        raise
    except Exception as e:
        Logger.print_error(f"Descarga fallida! Ocurrió un error: {e}")
        raise
def download_progress(block_num, block_size, total_size) -> None:
    """
    Método de informe para la llamada al método urllib.request.urlretrieve() en download_file() |
    :param block_num:
    :param block_size:
    :param total_size: tamaño total del archivo en bytes
    :return: None
    """
    downloaded = block_num * block_size
    percent = 100 if downloaded >= total_size else downloaded / total_size * 100
    mb = 1024 * 1024
    progress = int(percent / 5)
    remaining = "-" * (20 - progress)
    dl = f"\rDescargando: [{'#' * progress}{remaining}]{percent:.2f}% ({downloaded / mb:.2f}/{total_size / mb:.2f}MB)"
    sys.stdout.write(dl)
    sys.stdout.flush()


def set_nginx_permissions() -> None:
    """
    Verifica si los permisos del directorio principal del usuario
    conceden derechos de ejecución al grupo y a otros y los establece si no están configurados.
    Permisos requeridos para que NGINX pueda servir Mainsail/Fluidd.
    Esto parece haberse vuelto necesario con Ubuntu 21+. |
    :return: None
    """
    cmd = f"ls -ld {Path.home()} | cut -d' ' -f1"
    homedir_perm = run(cmd, shell=True, stdout=PIPE, text=True)
    permissions = homedir_perm.stdout

    if permissions.count("x") < 3:
        Logger.print_status("Concediendo los permisos requeridos a NGINX ...")
        run(["chmod", "og+x", Path.home()])
        Logger.print_ok("Permisos concedidos.")


def cmd_sysctl_service(name: str, action: SysCtlServiceAction) -> None:
    """
    Método auxiliar para ejecutar varias acciones para un servicio systemd específico. |
    :param name: el nombre del servicio
    :param action: Puede ser "start", "stop", "restart" o "disable"
    :return: None
    """
    try:
        Logger.print_status(f"{action.capitalize()} {name} ...")
        run(["sudo", "systemctl", action, name], stderr=PIPE, check=True)
        Logger.print_ok("¡OK!")
    except CalledProcessError as e:
        log = f"Fallo al {action} {name}: {e.stderr.decode()}"
        Logger.print_error(log)
        raise


def cmd_sysctl_manage(action: SysCtlManageAction) -> None:
    try:
        run(["sudo", "systemctl", action], stderr=PIPE, check=True)
    except CalledProcessError as e:
        log = f"Fallo al ejecutar {action}: {e.stderr.decode()}"
        Logger.print_error(log)
        raise


def unit_file_exists(
    name: str, suffix: Literal["service", "timer"], exclude: List[str] | None = None
) -> bool:
    """
    Verifica si existe un archivo de unidad systemd del sufijo proporcionado.
    :param name: el nombre del archivo de unidad
    :param suffix: sufijo del archivo de unidad, puede ser "service" o "timer"
    :param exclude: Lista de cadenas de nombres a excluir
    :return: True si el archivo de unidad existe, False en caso contrario
    """
    exclude = exclude or []
    pattern = re.compile(f"^{name}(-[0-9a-zA-Z]+)?.{suffix}$")
    service_list = [
        Path(SYSTEMD, service)
        for service in SYSTEMD.iterdir()
        if pattern.search(service.name) and not any(s in service.name for s in exclude)
    ]
    return any(service_list)


def log_process(process: Popen) -> None:
    """
    Método auxiliar para imprimir el stdout de un proceso en tiempo casi real en la consola.
    :param process: Proceso del que se desea registrar la salida
    :return: None
    """
    while True:
        if process.stdout is not None:
            reads = [process.stdout.fileno()]
            ret = select.select(reads, [], [])
            for fd in ret[0]:
                if fd == process.stdout.fileno():
                    line = process.stdout.readline()
                    if line:
                        print(line.strip(), flush=True)
                    else:
                        break

        if process.poll() is not None:
            break

def create_service_file(name: str, content: str) -> None:
    """
    Crea un archivo de servicio en la ruta proporcionada con el contenido proporcionado.
    :param name: el nombre del archivo de servicio
    :param content: el contenido del archivo de servicio
    :return: None
    """
    try:
        run(
            ["sudo", "tee", SYSTEMD.joinpath(name)],
            input=content.encode(),
            stdout=DEVNULL,
            check=True,
        )
        Logger.print_ok(f"Archivo de servicio creado: {SYSTEMD.joinpath(name)}")
    except CalledProcessError as e:
        Logger.print_error(f"Error creando archivo de servicio: {e}")
        raise


def create_env_file(path: Path, content: str) -> None:
    """
    Crea un archivo .env en la ruta proporcionada con el contenido proporcionado.
    :param path: la ruta del archivo .env
    :param content: el contenido del archivo .env
    :return: None
    """
    try:
        with open(path, "w") as env_file:
            env_file.write(content)
        Logger.print_ok(f"Archivo .env creado: {path}")
    except OSError as e:
        Logger.print_error(f"Error creando archivo .env: {e}")
        raise


def remove_system_service(service_name: str) -> None:
    """
    Deshabilita y elimina un servicio systemd
    :param service_name: nombre del archivo de unidad de servicio - debe terminar con '.service'
    :return: None
    """
    try:
        if not service_name.endswith(".service"):
            raise ValueError(f"service_name '{service_name}' debe terminar con '.service'")

        file: Path = SYSTEMD.joinpath(service_name)
        if not file.exists() or not file.is_file():
            Logger.print_info(f"Servicio '{service_name}' no existe! Saltado ...")
            return

        Logger.print_status(f"Eliminando {service_name} ...")
        cmd_sysctl_service(service_name, "stop")
        cmd_sysctl_service(service_name, "disable")
        remove_with_sudo(file)
        cmd_sysctl_manage("daemon-reload")
        cmd_sysctl_manage("reset-failed")
        Logger.print_ok(f"{service_name} eliminado con éxito!")
    except Exception as e:
        Logger.print_error(f"Error eliminando {service_name}: {e}")
        raise


def get_service_file_path(instance_type: type, suffix: str) -> Path:
    from utils.common import convert_camelcase_to_kebabcase

    if not isinstance(instance_type, type):
        raise ValueError("instance_type debe ser una clase")

    name: str = convert_camelcase_to_kebabcase(instance_type.__name__)
    if suffix != "":
        name += f"-{suffix}"

    file_path: Path = SYSTEMD.joinpath(f"{name}.service")

    return file_path


def get_distro_info() -> Tuple[str, str]:
    distro_info: str = check_output(["cat", "/etc/os-release"]).decode().strip()

    if not distro_info:
        raise ValueError("Error leyendo la información de la distribución!")

    distro_id: str = ""
    distro_id_like: str = ""
    distro_version: str = ""

    for line in distro_info.split("\n"):
        if line.startswith("ID="):
            distro_id = line.split("=")[1].strip('"').strip()
        if line.startswith("ID_LIKE="):
            distro_id_like = line.split("=")[1].strip('"').strip()
        if line.startswith("VERSION_ID="):
            distro_version = line.split("=")[1].strip('"').strip()

    if distro_id == "raspbian":
        distro_id = distro_id_like

    if not distro_id:
        raise ValueError("Error leyendo el ID de la distribución!")
    if not distro_version:
        raise ValueError("Error leyendo la versión de la distribución!")

    return distro_id.lower(), distro_version