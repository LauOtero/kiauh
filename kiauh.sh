#!/usr/bin/env bash

#=======================================================================#
# Copyright (C) 2020 - 2024 Dominik Willner <th33xitus@gmail.com>       #
#                                                                       #
# Este archivo es parte de KIAUH - Asistente de Instalación y Actualización de Klipper   #
# https://github.com/dw-0/kiauh                                         #
#                                                                       #
# Este archivo puede distribuirse bajo los términos de la licencia GNU GPLv3 #
#=======================================================================#

set -e
clear -x

# make sure we have the correct permissions while running the script
umask 022

### sourcing all additional scripts
KIAUH_SRCDIR="$(dirname -- "$(readlink -f "${BASH_SOURCE[0]}")")"
for script in "${KIAUH_SRCDIR}/scripts/"*.sh; do . "${script}"; done
for script in "${KIAUH_SRCDIR}/scripts/ui/"*.sh; do . "${script}"; done

#===================================================#
#=================== UPDATE KIAUH ==================#
#===================================================#

function update_kiauh() {
  status_msg "Actualizando KIAUH ..."

  cd "${KIAUH_SRCDIR}"
  git reset --hard && git pull

  ok_msg "¡Actualización completada! Por favor reinicie KIAUH."
  exit 0
}

#===================================================#
#=================== KIAUH STATUS ==================#
#===================================================#

function kiauh_update_avail() {
  [[ ! -d "${KIAUH_SRCDIR}/.git" ]] && return
  local origin head

  cd "${KIAUH_SRCDIR}"

  ### abort if not on master branch
  ! git branch -a | grep -q "\* master" && return

  ### compare commit hash
  git fetch -q
  origin=$(git rev-parse --short=8 origin/master)
  head=$(git rev-parse --short=8 HEAD)

  if [[ ${origin} != "${head}" ]]; then
    echo "true"
  fi
}

function save_startup_version() {
  local launch_version

  echo "${1}"

  sed -i "/^version_to_launch=/d" "${INI_FILE}"
  sed -i '$a'"version_to_launch=${1}" "${INI_FILE}"
}

function kiauh_update_dialog() {
  [[ ! $(kiauh_update_avail) == "true" ]] && return
  top_border
  echo -e "|${green}         ¡Nueva actualización de KIAUH disponible!         ${white}|"
  hr
  echo -e "|${green}  Ver Cambios: https://git.io/JnmlX                     ${white}|"
  blank_line
  echo -e "|${yellow}  Se recomienda mantener KIAUH actualizado. Las          ${white}|"
  echo -e "|${yellow}  actualizaciones usualmente contienen correcciones,    ${white}|"
  echo -e "|${yellow}  cambios importantes o nuevas características.          ${white}|"
  bottom_border

  local yn
  read -p "${cyan}###### Do you want to update now? (Y/n):${white} " yn
  while true; do
    case "${yn}" in
     Y|y|Yes|yes|"")
       do_action "update_kiauh"
       break;;
     N|n|No|no)
       break;;
     *)
       deny_action "kiauh_update_dialog";;
    esac
  done
}

function launch_kiauh_v5() {
    main_menu
}

function launch_kiauh_v6() {
  local entrypoint
  python3 "${entrypoint}/kiauh.py"
  
  if ! command -v python3 &>/dev/null || [[ $(python3 -V | cut -d " " -f2 | cut -d "." -f2) -lt 8 ]]; then
    echo "Python 3.8 or higher is not installed!"
    echo "Please install Python 3.8 or higher and try again."
    exit 1
  fi

  entrypoint=$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")

  export PYTHONPATH="${entrypoint}"

  clear -x
  python3 "${entrypoint}/kiauh.py"
}

function main() {
  read_kiauh_ini "${FUNCNAME[0]}"

  if [[ ${version_to_launch} -eq 5 ]]; then
    launch_kiauh_v5
  elif [[ ${version_to_launch} -eq 6 ]]; then
    launch_kiauh_v6
  else
    top_border
    echo -e "|         ${green}¡KIAUH v6.0.0-alpha1 está disponible ahora!${white}         |"
    hr
    echo -e "|         Ver Cambios: ${magenta}https://git.io/JnmlX${white}          |"
    blank_line
    echo -e "| KIAUH v6 fue completamente reescrito desde cero.      |"
    echo -e "| Está basado en Python 3.8 y tiene muchas mejoras.      |"
    blank_line
    echo -e "| ${yellow}NOTA: La versión 6 sigue en alpha, ¡puede tener errores!${white} |"
    echo -e "| ${yellow}Aún así, tus comentarios y reportes de errores son     ${white}|"
    echo -e "| ${yellow}muy apreciados y ayudarán a finalizar el lanzamiento.${white} |"
    hr
    echo -e "| ¿Te gustaría probar KIAUH v6?                        |"
    echo -e "| 1) Sí                                                 |"
    echo -e "| 2) No                                                 |"
    echo -e "| 3) Sí, recordar mi elección para la próxima vez       |"
    echo -e "| 4) No, recordar mi elección para la próxima vez       |"
    quit_footer
    while true; do
      read -p "${cyan}###### Select action:${white} " -e input
      case "${input}" in
        1)
          launch_kiauh_v6
          break;;
        2)
          launch_kiauh_v5
          break;;
        3)
          save_startup_version 6
          launch_kiauh_v6
          break;;
        4)
          save_startup_version 5
          launch_kiauh_v5
          break;;
        Q|q)
          echo -e "${green}###### ¡Felices impresiones! ######${white}"; echo
          exit 0;;
        *)
          error_msg "Invalid Input!\n";;
      esac
    done && input=""
  fi
}

check_if_ratos
check_euid
init_logfile
set_globals
kiauh_update_dialog
read_kiauh_ini
init_ini
main