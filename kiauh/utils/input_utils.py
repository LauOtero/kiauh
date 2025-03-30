# ======================================================================= #
#  Copyright (C) 2020 - 2025 Dominik Willner <th33xitus@gmail.com>        #
#                                                                         #
#  Este archivo es parte de KIAUH - Klipper Installation And Update Helper #
#  https://github.com/dw-0/kiauh                                          #
#                                                                         #
#  Este archivo puede distribuirse bajo los términos de la licencia GNU GPLv3 #
# ======================================================================= #
from __future__ import annotations

import re
from typing import Dict, List

from core.constants import INVALID_CHOICE
from core.logger import Logger
from core.types.color import Color


def get_confirm(question: str, default_choice=True, allow_go_back=False) -> bool | None:
    """
    Método auxiliar para validar la entrada del usuario de confirmación (sí/no). |
    :param question: La pregunta a mostrar
    :param default_choice: Un valor predeterminado si se envía la entrada sin especificar
    :param allow_go_back: Navegar hacia atrás a un diálogo anterior
    :return: Verdadero o Falso, o Ninguno en caso de volver
    """
    opciones_confirmar = ["s", "si"]
    opciones_rechazar = ["n", "no"]
    opciones_volver = ["b", "B"]

    if default_choice:
        def_choice = "(S/n)"
        opciones_confirmar.append("")
    else:
        def_choice = "(s/N)"
        opciones_rechazar.append("")

    while True:
        eleccion = (
            input(format_question(question + f" {def_choice}", None)).strip().lower()
        )

        if eleccion in opciones_confirmar:
            return True
        elif eleccion in opciones_rechazar:
            return False
        elif allow_go_back and eleccion in opciones_volver:
            return None
        else:
            Logger.print_error(INVALID_CHOICE)


def get_number_input(
    question: str,
    min_count: int,
    max_count: int | None = None,
    default: int | None = None,
    allow_go_back: bool = False,
) -> int | None:
    """
    Método auxiliar para obtener una entrada numérica del usuario
    :param question: La pregunta a mostrar
    :param min_count: El valor más bajo permitido
    :param max_count: El valor más alto permitido (o Ninguno)
    :param default: Valor predeterminado opcional
    :param allow_go_back: Navegar hacia atrás a un diálogo anterior
    :return: La entrada numérica validada, o Ninguno en caso de volver
    """
    opciones_volver = ["b", "B"]
    _question = format_question(question, default)
    while True:
        _entrada = input(_question)
        if allow_go_back and _entrada in opciones_volver:
            return None

        if _entrada == "" and default is not None:
            return default

        try:
            return validate_number_input(_entrada, min_count, max_count)
        except ValueError:
            Logger.print_error(INVALID_CHOICE)


def get_string_input(
    question: str,
    regex: str | None = None,
    exclude: List[str] | None = None,
    allow_empty: bool = False,
    allow_special_chars: bool = False,
    default: str | None = None,
) -> str:
    """
    Método auxiliar para obtener una entrada de cadena del usuario
    :param question: La pregunta a mostrar
    :param regex: Un patrón de expresión regular opcional para validar la entrada
    :param exclude: Lista de cadenas que no están permitidas
    :param allow_empty: Si se permite entrada vacía
    :param allow_special_chars: Si se permiten caracteres especiales en la entrada
    :param default: Valor predeterminado opcional
    :return: El valor de cadena validado
    """
    _excluir = [] if exclude is None else exclude
    _question = format_question(question, default)
    _patron = re.compile(regex) if regex is not None else None
    while True:
        _entrada = input(_question)

        if default is not None and _entrada == "":
            return default
        elif _entrada == "" and not allow_empty:
            Logger.print_error("La entrada no debe estar vacía!")
        elif _patron is not None and _patron.match(_entrada):
            return _entrada
        elif _entrada.lower() in _excluir:
            Logger.print_error("Este valor ya está en uso/reservado.")
        elif allow_special_chars:
            return _entrada
        elif not allow_special_chars and _entrada.isalnum():
            return _entrada
        else:
            Logger.print_error(INVALID_CHOICE)


def get_selection_input(question: str, option_list: List | Dict, default=None) -> str:
    """
    Método auxiliar para obtener una selección de una lista de opciones del usuario
    :param question: La pregunta a mostrar
    :param option_list: La lista de opciones que el usuario puede seleccionar
    :param default: Valor predeterminado opcional
    :return: La opción seleccionada por el usuario
    """
    while True:
        _entrada = input(format_question(question, default)).strip().lower()

        if isinstance(option_list, list):
            if _entrada in option_list:
                return _entrada
        elif isinstance(option_list, dict):
            if _entrada in option_list.keys():
                return _entrada
        else:
            raise ValueError("Tipo de option_list inválido")

        Logger.print_error("Opción inválida. Por favor, seleccione una opción válida.", False)


def format_question(question: str, default=None) -> str:
    """
    Método auxiliar para tener un formato estándar de preguntas |
    :param question: La pregunta a mostrar
    :param default: Si está definido, se mostrará la opción predeterminada al usuario
    :return: La cadena de pregunta formateada
    """
    pregunta_formateada = question
    if default is not None:
        pregunta_formateada += f" (predeterminado={default})"

    return Color.apply(f"###### {pregunta_formateada}: ", Color.CYAN)


def validate_number_input(value: str, min_count: int, max_count: int | None) -> int:
    """
    Método auxiliar para una validación simple de entrada numérica. |
    :param value: El valor a validar
    :param min_count: El valor más bajo permitido
    :param max_count: El valor más alto permitido (o Ninguno)
    :return: El valor validado como Entero
    :raises: ValueError si el valor es inválido
    """
    if max_count is not None:
        if min_count <= int(value) <= max_count:
            return int(value)
    elif int(value) >= min_count:
        return int(value)

    raise ValueError