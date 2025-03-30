#!/usr/bin/env python3

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
import shutil
from pathlib import Path
from subprocess import DEVNULL, PIPE, CalledProcessError, call, check_output, run
from typing import List
from zipfile import ZipFile

from core.decorators import deprecated
from core.logger import Logger


def check_file_exist(file_path: Path, sudo=False) -> bool:
    """
    Función auxiliar para verificar la existencia de un archivo |
    :param file_path: la ruta absoluta del archivo a verificar
    :param sudo: usar sudo si es necesario
    :return: True si el archivo existe, de lo contrario False
    """
    if sudo:
        command = ["sudo", "find", file_path.as_posix()]
        try:
            check_output(command, stderr=DEVNULL)
            return True
        except CalledProcessError:
            return False
    else:
        if os.access(file_path, os.F_OK):
            return file_path.exists()
        else:
            return False


def create_symlink(source: Path, target: Path, sudo=False) -> None:
    try:
        cmd = ["ln", "-sf", source.as_posix(), target.as_posix()]
        if sudo:
            cmd.insert(0, "sudo")
        run(cmd, stderr=PIPE, check=True)
    except CalledProcessError as e:
        Logger.print_error(f"Fallo al crear enlace simbólico: {e}")
        raise


def remove_with_sudo(files: Path | List[Path]) -> bool:
    _files = []
    _removed = []
    if isinstance(files, list):
        _files = files
    else:
        _files.append(files)

    for f in _files:
        try:
            cmd = ["sudo", "find", f.as_posix()]
            if call(cmd, stderr=DEVNULL, stdout=DEVNULL) == 1:
                Logger.print_info(f"El archivo '{f}' no existe. Saltado ...")
                continue
            cmd = ["sudo", "rm", "-rf", f.as_posix()]
            run(cmd, stderr=PIPE, check=True)
            Logger.print_ok(f"El archivo '{f}' fue eliminado con éxito!")
            _removed.append(f)
        except CalledProcessError as e:
            Logger.print_error(f"Error al eliminar el archivo '{f}': {e}")

    return len(_removed) > 0


@deprecated(info="Usa remove_with_sudo en su lugar", replaced_by=remove_with_sudo)
def remove_file(file_path: Path, sudo=False) -> None:
    try:
        cmd = f"{'sudo ' if sudo else ''}rm -f {file_path}"
        run(cmd, stderr=PIPE, check=True, shell=True)
    except CalledProcessError as e:
        log = f"No se puede eliminar el archivo {file_path}: {e.stderr.decode()}"
        Logger.print_error(log)
        raise


def run_remove_routines(file: Path) -> bool:
    try:
        if not file.is_symlink() and not file.exists():
            Logger.print_info(f"El archivo '{file}' no existe. Saltado ...")
            return False

        if file.is_dir():
            shutil.rmtree(file)
        elif file.is_file() or file.is_symlink():
            file.unlink()
        else:
            Logger.print_error(f"El archivo '{file}' ni es un archivo ni un directorio!")
            return False
        Logger.print_ok(f"El archivo '{file}' fue eliminado con éxito!")
        return True
    except OSError as e:
        Logger.print_error(f"Incapaz de eliminar '{file}':\n{e}")
        try:
            Logger.print_info("Intentando eliminar con sudo ...")
            if remove_with_sudo(file):
                Logger.print_ok(f"El archivo '{file}' fue eliminado con éxito!")
                return True
        except CalledProcessError as e:
            Logger.print_error(f"Error al eliminar '{file}' con sudo:\n{e}")
            Logger.print_error("Elimina este directorio manualmente!")
            return False


def unzip(filepath: Path, target_dir: Path) -> None:
    """
    Función auxiliar para descomprimir un archivo zip en un directorio de destino |
    :param filepath: la ruta al archivo zip a descomprimir
    :param target_dir: el directorio de destino para extraer los archivos
    :return: None
    """
    with ZipFile(filepath, "r") as _zip:
        _zip.extractall(target_dir)


def create_folders(dirs: List[Path]) -> None:
    try:
        for _dir in dirs:
            if _dir.exists():
                continue
            _dir.mkdir(exist_ok=True)
            Logger.print_ok(f"Creado directorio '{_dir}'!")
    except OSError as e:
        Logger.print_error(f"Error creando directorios: {e}")
        raise


def get_data_dir(instance_type: type, suffix: str) -> Path:
    from utils.sys_utils import get_service_file_path
    # si el archivo de servicio existe, leemos la ruta del directorio de datos desde él
    # esto también garantiza la compatibilidad con instancias anteriores a v6.0.0
    service_file_path: Path = get_service_file_path(instance_type, suffix)
    if service_file_path and service_file_path.exists():
        with open(service_file_path, "r") as service_file:
            lines = service_file.readlines()
            for line in lines:
                pattern = r"^EnvironmentFile=(.+)(/systemd/.+\.env)"
                match = re.search(pattern, line)
                if match:
                    return Path(match.group(1))

    if suffix != "":
        # este es el nuevo esquema de nomenclatura de directorios de datos introducido en v6.0.0
        return Path.home().joinpath(f"printer_{suffix}_data")

    return Path.home().joinpath("printer_data")