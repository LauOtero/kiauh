# ======================================================================= #
#  Copyright (C) 2020 - 2025 Dominik Willner <th33xitus@gmail.com>        #
#                                                                         #
#  Este archivo es parte de KIAUH - Klipper Installation And Update Helper #
#  https://github.com/dw-0/kiauh                                          #
#                                                                         #
#  Este archivo puede ser distribuido bajo los términos de GNU GPLv3      #
# ======================================================================= #
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import List, Tuple

from core.logger import Logger
from core.submodules.simple_config_parser.src.simple_config_parser.simple_config_parser import (
    SimpleConfigParser,
)
from utils.instance_type import InstanceType

OpcionConfig = Tuple[str, str]


def agregar_seccion_config(
    seccion: str,
    instancias: List[InstanceType],
    opciones: List[OpcionConfig] | None = None,
) -> None:
    if not instancias:
        return

    for instancia in instancias:
        archivo_cfg = instancia.cfg_file
        Logger.print_status(f"Agregando sección '[{seccion}]' a '{archivo_cfg}' ...")

        if not Path(archivo_cfg).exists():
            Logger.print_warn(f"'{archivo_cfg}' no encontrado!")
            continue

        scp = SimpleConfigParser()
        scp.read_file(archivo_cfg)
        if scp.has_section(seccion):
            Logger.print_info("La sección ya existe. Omitiendo ...")
            continue

        scp.add_section(seccion)

        if opciones is not None:
            for opcion in reversed(opciones):
                scp.set_option(seccion, opcion[0], opcion[1])

        scp.write_file(archivo_cfg)

        Logger.print_ok("¡OK!")


def agregar_seccion_config_arriba(seccion: str, instancias: List[InstanceType]) -> None:
    # TODO: this could be implemented natively in SimpleConfigParser
    for instancia in instancias:
        tmp_cfg = tempfile.NamedTemporaryFile(mode="w", delete=False)
        ruta_tmp_cfg = Path(tmp_cfg.name)
        scp = SimpleConfigParser()
        scp.read_file(ruta_tmp_cfg)
        scp.add_section(seccion)
        scp.write_file(ruta_tmp_cfg)
        tmp_cfg.close()

        archivo_cfg = instancia.cfg_file
        with open(archivo_cfg, "r") as org:
            contenido_org = org.readlines()
        with open(ruta_tmp_cfg, "a") as tmp:
            tmp.writelines(contenido_org)

        archivo_cfg.unlink()
        shutil.move(ruta_tmp_cfg, archivo_cfg)

        Logger.print_ok("¡OK!")


def eliminar_seccion_config(
    seccion: str, instancias: List[InstanceType]
) -> List[InstanceType]:
    eliminado_de: List[instancias] = []
    for instancia in instancias:
        archivo_cfg = instancia.cfg_file
        Logger.print_status(f"Eliminando sección '[{seccion}]' de '{archivo_cfg}' ...")

        if not Path(archivo_cfg).exists():
            Logger.print_warn(f"'{archivo_cfg}' no encontrado!")
            continue

        scp = SimpleConfigParser()
        scp.read_file(archivo_cfg)
        if not scp.has_section(seccion):
            Logger.print_info("La sección no existe. Omitiendo ...")
            continue

        scp.remove_section(seccion)
        scp.write_file(archivo_cfg)

        eliminado_de.append(instancia)
        Logger.print_ok("¡OK!")

    return eliminado_de
