# ======================================================================= #
#  Copyright (C) 2020 - 2025 Dominik Willner <th33xitus@gmail.com>        #
#                                                                         #
#  Este archivo es parte de KIAUH - Klipper Installation And Update Helper #
#  https://github.com/dw-0/kiauh                                          #
#                                                                         #
#  Este archivo puede ser distribuido bajo los términos de GNU GPLv3      #
# ======================================================================= #
from __future__ import annotations

from pathlib import Path
import shutil
from typing import Literal

from components.klipper import (
    KLIPPER_BACKUP_DIR,
    KLIPPER_DIR,
    KLIPPER_ENV_DIR,
    KLIPPER_REQ_FILE,
)
from components.klipper.klipper import Klipper
from components.klipper.klipper_utils import install_klipper_packages
from components.moonraker import (
    MOONRAKER_BACKUP_DIR,
    MOONRAKER_DIR,
    MOONRAKER_ENV_DIR,
    MOONRAKER_REQ_FILE,
)
from components.moonraker.moonraker import Moonraker
from components.moonraker.moonraker_setup import install_moonraker_packages
from core.backup_manager.backup_manager import BackupManager, BackupManagerException
from core.instance_manager.instance_manager import InstanceManager
from core.logger import Logger
from core.settings.kiauh_settings import RepoSettings
from utils.git_utils import GitException, get_repo_name, git_clone_wrapper
from utils.instance_utils import get_instances
from utils.sys_utils import (
    VenvCreationFailedException,
    create_python_venv,
    install_python_requirements,
)


class RepoSwitchFailedException(Exception):
    pass


def run_switch_repo_routine(
    name: Literal["klipper", "moonraker"], repo_settings: RepoSettings
) -> None:
    repo_dir: Path = KLIPPER_DIR if name == "klipper" else MOONRAKER_DIR
    env_dir: Path = KLIPPER_ENV_DIR if name == "klipper" else MOONRAKER_ENV_DIR
    req_file = KLIPPER_REQ_FILE if name == "klipper" else MOONRAKER_REQ_FILE
    backup_dir: Path = KLIPPER_BACKUP_DIR if name == "klipper" else MOONRAKER_BACKUP_DIR
    _type = Klipper if name == "klipper" else Moonraker

    # paso 1: detener todas las instancias
    Logger.print_status(f"Deteniendo todas las instancias de {_type.__name__} ...")
    instances = get_instances(_type)
    InstanceManager.stop_all(instances)

    repo_dir_backup_path: Path | None = None
    env_dir_backup_path: Path | None = None

    try:
        # paso 2: respaldar repositorio y entorno antiguos
        org, _ = get_repo_name(repo_dir)
        backup_dir = backup_dir.joinpath(org)
        bm = BackupManager()
        repo_dir_backup_path = bm.backup_directory(
            repo_dir.name,
            repo_dir,
            backup_dir,
        )
        env_dir_backup_path = bm.backup_directory(
            env_dir.name,
            env_dir,
            backup_dir,
        )

        # paso 3: leer URL del repositorio y rama desde configuración
        repo_url = repo_settings.repo_url
        branch = repo_settings.branch

        if not (repo_url or branch):
            error = f"¡URL del repositorio ({repo_url}) o rama ({branch}) inválidos!"
            raise ValueError(error)

        # paso 4: clonar nuevo repositorio
        git_clone_wrapper(repo_url, repo_dir, branch, force=True)

        # paso 5: instalar dependencias del sistema operativo
        if name == "klipper":
            install_klipper_packages()
        elif name == "moonraker":
            install_moonraker_packages()

        # paso 6: recrear entorno virtual de python
        Logger.print_status(f"Recreando entorno virtual de {_type.__name__} ...")
        if not create_python_venv(env_dir, force=True):
            raise GitException(f"Error al recrear entorno virtual para {_type.__name__}")
        else:
            install_python_requirements(env_dir, req_file)

        Logger.print_ok(f"¡Cambiado a {repo_url} en la rama {branch}!")

    except BackupManagerException as e:
        Logger.print_error(f"Error durante el respaldo del repositorio: {e}")
        raise RepoSwitchFailedException(e)

    except (GitException, VenvCreationFailedException) as e:
        # si algo sale mal durante la clonación o recreación del entorno virtual,
        # restauramos el respaldo del repositorio y entorno
        Logger.print_error(f"Error durante el cambio de repositorio: {e}", start="\n")
        Logger.print_status(f"Restaurando último respaldo de {_type.__name__} ...")
        _restore_repo_backup(
            _type.__name__,
            env_dir,
            env_dir_backup_path,
            repo_dir,
            repo_dir_backup_path,
        )

    except RepoSwitchFailedException as e:
        Logger.print_error(f"Algo salió mal: {e}")
        return

    Logger.print_status(f"Reiniciando todas las instancias de {_type.__name__} ...")
    InstanceManager.start_all(instances)


def _restore_repo_backup(
    name: str,
    env_dir: Path,
    env_dir_backup_path: Path | None,
    repo_dir: Path,
    repo_dir_backup_path: Path | None,
) -> None:
    if not repo_dir_backup_path or not env_dir_backup_path:
        raise RepoSwitchFailedException(
            f"¡No se puede restaurar el respaldo de {name}! ¡La ruta del directorio de respaldos es None!"
        )

    try:
        if repo_dir.exists():
            shutil.rmtree(repo_dir)
            shutil.copytree(repo_dir_backup_path, repo_dir)
        if env_dir.exists():
            shutil.rmtree(env_dir)
            shutil.copytree(env_dir_backup_path, env_dir)
        Logger.print_warn(f"¡Respaldo de {name} restaurado exitosamente!")
    except Exception as e:
        raise RepoSwitchFailedException(f"Error al restaurar respaldo: {e}")
