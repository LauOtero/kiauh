# ======================================================================= #
#  Copyright (C) 2020 - 2025 Dominik Willner <th33xitus@gmail.com>        #
#                                                                         #
#  Este archivo es parte de KIAUH - Asistente de Instalación y           #
#  Actualización de Klipper                                              #
#  https://github.com/dw-0/kiauh                                          #
#                                                                         #
#  Este archivo puede ser distribuido bajo los términos de la            #
#  licencia GNU GPLv3                                                     #
# ======================================================================= #

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Literal, Set

from components.klipper.klipper import Klipper
from components.moonraker.moonraker import Moonraker
from core.constants import (
    GLOBAL_DEPS,
    PRINTER_DATA_BACKUP_DIR,
)
from core.logger import DialogType, Logger
from core.types.color import Color
from core.types.component_status import ComponentStatus, StatusCode
from utils.git_utils import (
    get_current_branch,
    get_local_commit,
    get_local_tags,
    get_remote_commit,
    get_repo_name,
)
from utils.instance_utils import get_instances
from utils.sys_utils import (
    check_package_install,
    install_system_packages,
    update_system_package_lists,
)


def get_kiauh_version() -> str:
    """
    Método auxiliar para obtener la versión actual de KIAUH leyendo la última etiqueta
    :return: cadena de la última etiqueta
    """
    lastest_tag: str = get_local_tags(Path(__file__).parent.parent)[-1]
    return lastest_tag


def convert_camelcase_to_kebabcase(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "-", name).lower()


def get_current_date() -> Dict[Literal["date", "time"], str]:
    """
    Obtener la fecha actual |
    :return: Diccionario que contiene un par clave:valor de fecha y hora
    """
    now: datetime = datetime.today()
    date: str = now.strftime("%Y%m%d")
    time: str = now.strftime("%H%M%S")

    return {"date": date, "time": time}


def check_install_dependencies(
    deps: Set[str] | None = None, include_global: bool = True
) -> None:
    """
    Método auxiliar común para verificar si las dependencias están instaladas
    y si no, instalarlas automáticamente |
    :param include_global: Si se incluyen o no las dependencias globales
    :param deps: Lista de nombres de paquetes como cadenas para verificar si están instalados
    :return: None
    """
    if deps is None:
        deps = set()

    if include_global:
        deps.update(GLOBAL_DEPS)

    requirements = check_package_install(deps)
    if requirements:
        Logger.print_status("Instalando dependencias ...")
        Logger.print_info("Los siguientes paquetes necesitan instalación:")
        for r in requirements:
            print(Color.apply(f"● {r}", Color.CYAN))
        update_system_package_lists(silent=False)
        install_system_packages(requirements)


def get_install_status(
    repo_dir: Path,
    env_dir: Path | None = None,
    instance_type: type | None = None,
    files: List[Path] | None = None,
) -> ComponentStatus:
    """
    Método auxiliar para obtener el estado de instalación de los componentes de software
    :param repo_dir: el directorio del repositorio
    :param env_dir: el directorio del entorno python
    :param instance_type: El tipo de componente
    :param files: Lista de archivos opcionales para verificar su existencia
    :return: Diccionario con cadena de estado, código de estado y conteo de instancias
    """
    from utils.instance_utils import get_instances

    checks = []
    branch: str = ""

    if repo_dir.exists():
        checks.append(True)
        branch = get_current_branch(repo_dir)

    if env_dir is not None:
        checks.append(env_dir.exists())

    instances = 0
    if instance_type is not None:
        instances = len(get_instances(instance_type))
        checks.append(instances > 0)

    if files is not None:
        for f in files:
            checks.append(f.exists())

    status: StatusCode
    if checks and all(checks):
        status = 2  # instalado
    elif not any(checks):
        status = 0  # no instalado
    else:
        status = 1  # incompleto

    org, repo = get_repo_name(repo_dir)
    return ComponentStatus(
        status=status,
        instances=instances,
        owner=org,
        repo=repo,
        branch=branch,
        local=get_local_commit(repo_dir),
        remote=get_remote_commit(repo_dir),
    )


def backup_printer_config_dir() -> None:
    # importación local para prevenir importación circular
    from core.backup_manager.backup_manager import BackupManager

    instances: List[Klipper] = get_instances(Klipper)
    bm = BackupManager()

    if not instances:
        Logger.print_info("¡No se puede encontrar el directorio para respaldar!")
        Logger.print_info("¿No hay instancias de Klipper instaladas?")
        return

    for instance in instances:
        bm.backup_directory(
            instance.data_dir.name,
            source=instance.base.cfg_dir,
            target=PRINTER_DATA_BACKUP_DIR,
        )


def moonraker_exists(name: str = "") -> List[Moonraker]:
    """
    Método auxiliar para verificar si existe una instancia de Moonraker
    :param name: Nombre opcional de un instalador donde se realiza la verificación
    :return: True si existe al menos una instancia de Moonraker, False en caso contrario
    """
    mr_instances: List[Moonraker] = get_instances(Moonraker)

    info = (
        f"{name} requiere que Moonraker esté instalado"
        if name
        else "Se requiere una instalación de Moonraker"
    )

    if not mr_instances:
        Logger.print_dialog(
            DialogType.WARNING,
            [
                "¡No se encontraron instancias de Moonraker!",
                f"{info}. ¡Por favor, instale Moonraker primero!",
            ],
        )
        return []
    return mr_instances


def trunc_string(input_str: str, length: int) -> str:
    if len(input_str) > length:
        return f"{input_str[: length - 3]}..."
    return input_str
