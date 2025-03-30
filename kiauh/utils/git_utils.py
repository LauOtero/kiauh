from __future__ import annotations

import json
import re
import shutil
import urllib.request
from http.client import HTTPResponse
from json import JSONDecodeError
from pathlib import Path
from subprocess import DEVNULL, PIPE, CalledProcessError, check_output, run
from typing import List, Tuple, Type

from core.instance_manager.instance_manager import InstanceManager
from core.logger import Logger
from utils.input_utils import get_confirm, get_number_input
from utils.instance_type import InstanceType
from utils.instance_utils import get_instances


class GitException(Exception):
    pass


def git_clone_wrapper(
    repo: str, target_dir: Path, branch: str | None = None, force: bool = False) -> None:
    """
    Clona un repositorio desde la URL dada y verifica la rama especificada si se proporciona.
    La clonación se realizará con la bandera '--filter=blob:none' para realizar una clonación sin blobs.

    :param repo: La URL del repositorio a clonar.
    :param branch: La rama a verificar. Si es None, master o main, no se realizará verificación.
    :param target_dir: El directorio donde se clonará el repositorio.
    :param force: Forzar la clonación del repositorio incluso si ya existe.
    :return: None
    """
    log = f"Clonando repositorio desde '{repo}'"
    Logger.print_status(log)
    try:
        if Path(target_dir).exists():
            question = f"'{target_dir}' ya existe. ¿Sobrescribir?"
            if not force and not get_confirm(question, default_choice=False):
                Logger.print_info("Omitiendo clonación del repositorio ...")
                return
            shutil.rmtree(target_dir)

        git_cmd_clone(repo, target_dir, blobless=True)

        if branch not in ("master", "main"):
            git_cmd_checkout(branch, target_dir)

    except CalledProcessError:
        log = "Ocurrió un error inesperado durante la clonación del repositorio."
        Logger.print_error(log)
        raise GitException(log)
    except OSError as e:
        Logger.print_error(f"Error al eliminar el repositorio existente: {e.strerror}")
        raise GitException(f"Error al eliminar el repositorio existente: {e.strerror}")


def git_pull_wrapper(repo: str, target_dir: Path) -> None:
    """
    Una función que actualiza un repositorio usando git pull.

    :param repo: El repositorio a actualizar.
    :param target_dir: El directorio del repositorio.
    :return: None
    """
    Logger.print_status(f"Actualizando repositorio '{repo}' ...")
    try:
        git_cmd_pull(target_dir)
    except CalledProcessError:
        log = "Ocurrió un error inesperado durante la actualización del repositorio."
        Logger.print_error(log)
        return


def get_repo_name(repo: Path) -> Tuple[str, str]:
    """
    Método auxiliar para extraer la organización y nombre de un repositorio |
    :param repo: repositorio del cual extraer los valores
    :return: Cadena en forma de "<orga>/<nombre>" o None
    """
    if not repo.exists() or not repo.joinpath(".git").exists():
        return "-", "-"

    try:
        cmd = ["git", "-C", repo.as_posix(), "config", "--get", "remote.origin.url"]
        result: str = check_output(cmd, stderr=DEVNULL).decode(encoding="utf-8")
        substrings: List[str] = result.strip().split("/")[-2:]

        orga: str = substrings[0] if substrings[0] else "-"
        name: str = substrings[1] if substrings[1] else "-"

        return orga, name.replace(".git", "")

    except CalledProcessError:
        return "-", "-"


def get_current_branch(repo: Path) -> str:
    """
    Obtiene la rama actual de un repositorio Git local
    :param repo: Ruta al repositorio Git local
    :return: Rama actual
    """
    try:
        cmd = ["git", "branch", "--show-current"]
        result: str = check_output(cmd, stderr=DEVNULL, cwd=repo).decode(
            encoding="utf-8"
        )
        return result.strip() if result else "-"

    except CalledProcessError:
        return "-"


def get_local_tags(repo_path: Path, _filter: str | None = None) -> List[str]:
    """
    Obtiene todas las etiquetas de un repositorio Git local
    :param repo_path: Ruta al repositorio Git local
    :param _filter: Filtro opcional para filtrar las etiquetas
    :return: Lista de etiquetas
    """
    try:
        cmd: List[str] = ["git", "tag", "-l"]

        if _filter is not None:
            cmd.append(f"'${_filter}'")

        result: str = check_output(
            cmd,
            stderr=DEVNULL,
            cwd=repo_path.as_posix(),
        ).decode(encoding="utf-8")

        tags: List[str] = result.split("\n")[:-1]

        return sorted(
            tags,
            key=lambda x: [int(i) if i.isdigit() else i for i in re.split(r"(\d+)", x)],
        )

    except CalledProcessError:
        return []


def get_remote_tags(repo_path: str) -> List[str]:
    """
    Obtiene las etiquetas de un repositorio GitHub
    :param repo_path: ruta del repositorio GitHub - ej. `<propietario>/<nombre>`
    :return: Lista de etiquetas
    """
    try:
        url = f"https://api.github.com/repos/{repo_path}/tags"
        with urllib.request.urlopen(url) as r:
            response: HTTPResponse = r
            if response.getcode() != 200:
                Logger.print_error(
                    f"Error al recuperar etiquetas: código de estado HTTP {response.getcode()}"
                )
                return []

            data = json.loads(response.read())
            return [item["name"] for item in data]
    except (JSONDecodeError, TypeError) as e:
        Logger.print_error(f"Error al procesar la respuesta: {e}")
        raise


def get_latest_remote_tag(repo_path: str) -> str:
    """
    Obtiene la última etiqueta estable de un repositorio GitHub
    :param repo_path: ruta del repositorio GitHub - ej. `<propietario>/<nombre>`
    :return: etiqueta o cadena vacía
    """
    try:
        if len(latest_tag := get_remote_tags(repo_path)) > 0:
            return latest_tag[0]
        else:
            return ""
    except Exception:
        raise


def get_latest_unstable_tag(repo_path: str) -> str:
    """
    Obtiene la última etiqueta inestable (alpha, beta, rc) de un repositorio GitHub
    :param repo_path: ruta del repositorio GitHub - ej. `<propietario>/<nombre>`
    :return: etiqueta o cadena vacía
    """
    try:
        if (
            len(unstable_tags := [t for t in get_remote_tags(repo_path) if "-" in t])
            > 0
        ):
            return unstable_tags[0]
        else:
            return ""
    except Exception:
        Logger.print_error("Error al obtener la última etiqueta inestable")
        raise


def compare_semver_tags(tag1: str, tag2: str) -> bool:
    """
    Compara dos cadenas de versión semver.
    No admite la comparación de versiones preliminares (ej. 1.0.0-rc.1, 1.0.0-beta.1)
    :param tag1: Primera cadena de versión
    :param tag2: Segunda cadena de versión
    :return: True si tag1 es mayor que tag2, False en caso contrario
    """
    if tag1 == tag2:
        return False

    def parse_version(v) -> List[int]:
        return list(map(int, v[1:].split(".")))

    tag1_parts = parse_version(tag1)
    tag2_parts = parse_version(tag2)

    max_len = max(len(tag1_parts), len(tag2_parts))
    tag1_parts += [0] * (max_len - len(tag1_parts))
    tag2_parts += [0] * (max_len - len(tag2_parts))

    for part1, part2 in zip(tag1_parts, tag2_parts):
        if part1 != part2:
            return part1 > part2

    return False


def get_local_commit(repo: Path) -> str | None:
    if not repo.exists() or not repo.joinpath(".git").exists():
        return None

    try:
        cmd = "git describe HEAD --always --tags | cut -d '-' -f 1,2"
        return check_output(cmd, shell=True, text=True, cwd=repo).strip()
    except CalledProcessError:
        return None


def get_remote_commit(repo: Path) -> str | None:
    if not repo.exists() or not repo.joinpath(".git").exists():
        return None

    try:
        branch = get_current_branch(repo)
        cmd = f"git describe 'origin/{branch}' --always --tags | cut -d '-' -f 1,2"
        return check_output(
            cmd,
            shell=True,
            text=True,
            cwd=repo,
            stderr=DEVNULL,
        ).strip()
    except CalledProcessError:
        return None


def git_cmd_clone(repo: str, target_dir: Path, blobless: bool = False) -> None:
    """
    Clona un repositorio con clonación sin blobs opcional.

    :param repo: URL del repositorio a clonar.
    :param target_dir: Ruta donde se clonará el repositorio.
    :param blobless: Si es True, realiza una clonación sin blobs agregando la bandera '--filter=blob:none'.
    """
    try:
        command = ["git", "clone"]

        if blobless:
            command.append("--filter=blob:none")

        command += [repo, target_dir.as_posix()]

        run(command, check=True)
        Logger.print_ok("¡Clonación exitosa!")
    except CalledProcessError as e:
        error = e.stderr.decode() if e.stderr else "Error desconocido"
        log = f"Error al clonar repositorio {repo}: {error}"
        Logger.print_error(log)
        raise


def git_cmd_checkout(branch: str | None, target_dir: Path) -> None:
    if branch is None:
        return

    try:
        command = ["git", "checkout", f"{branch}"]
        run(command, cwd=target_dir, check=True)

        Logger.print_ok("¡Checkout exitoso!")
    except CalledProcessError as e:
        log = f"Error al hacer checkout de la rama {branch}: {e.stderr.decode()}"
        Logger.print_error(log)
        raise


def git_cmd_pull(target_dir: Path) -> None:
    try:
        command = ["git", "pull"]
        run(command, cwd=target_dir, check=True)
    except CalledProcessError as e:
        log = f"Error en git pull: {e.stderr.decode()}"
        Logger.print_error(log)
        raise


def rollback_repository(repo_dir: Path, instance: Type[InstanceType]) -> None:
    q1 = "¿Cuántos commits desea revertir?"
    amount = get_number_input(q1, 1, allow_go_back=True)

    instances = get_instances(instance)

    Logger.print_warn("¡No continúe si tiene impresiones en curso!", start="\n")
    Logger.print_warn(
        f"¡Todos los servicios de {instance.__name__} actualmente en ejecución serán detenidos!"
    )
    if not get_confirm(
        f"Revert {amount} {'commits' if amount > 1 else 'commit'}",
        default_choice=False,
        allow_go_back=True,
    ):
        Logger.print_info("Abortando reversión ...")
        return

    InstanceManager.stop_all(instances)

    try:
        cmd = ["git", "reset", "--hard", f"HEAD~{amount}"]
        run(cmd, cwd=repo_dir, check=True, stdout=PIPE, stderr=PIPE)
        Logger.print_ok(f"¡Se revirtieron {amount} commits!", start="\n")
    except CalledProcessError as e:
        Logger.print_error(f"Ocurrió un error durante la reversión del repositorio:\n{e}")

    InstanceManager.start_all(instances)
