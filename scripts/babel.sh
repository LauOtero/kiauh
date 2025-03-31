#!/bin/bash

# Configuración de rutas base
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
readonly BASE_DIR="$(dirname "$SCRIPT_DIR")"
cd "$BASE_DIR"  # Cambiamos al directorio base

readonly SRC_DIR="kiauh"  # Ruta relativa desde BASE_DIR
readonly LOCALE_DIR="kiauh/locale"  # Ruta relativa
readonly POT_FILE="${LOCALE_DIR}/templates/messages.pot"

# Crear directorios necesarios
mkdir -p "$(dirname "${POT_FILE}")"

# Función para procesar archivos de traducción
procesar_archivos_traduccion() {
    local input_file="$1"
    local temp_file="${input_file}.tmp"
    
    if [[ ! -f "$input_file" ]]; then
        echo "El archivo $input_file no existe."
        return 1
    fi
    
    awk '
    BEGIN {
        RS = ""; FS = "\n"; OFS = "\n"
    }
    {
        if ($0 ~ /^msgid /) {
            msgid = gensub(/^msgid /, "", "g")
            gsub(/"/, "", msgid)
            gsub(/\n/, "\\n", msgid)
            gsub(/\\n/, "\\\\n", msgid)
            print "msgid \"" msgid "\""
        } else if ($0 ~ /^msgstr /) {
            msgstr = gensub(/^msgstr /, "", "g")
            gsub(/"/, "", msgstr)
            gsub(/\n/, "\\n", msgstr)
            gsub(/\\n/, "\\\\n", msgstr)
            print "msgstr \"" msgstr "\""
        } else {
            print $0
        }
    }
    ' "$input_file" > "$temp_file"
    
    mv "$temp_file" "$input_file"
    echo "Procesado: $input_file"
}

# Process arguments
# Modify the process_args function to include path cleaning
process_args() {
    local extract=0 update=0 compile=0 lang=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -e|--extract)
                extract=1
                ;;
            -u|--update)
                update=1
                ;;
            -c|--compile)
                compile=1
                ;;
            -l|--lang)
                if [ -n "$2" ]; then
                    lang="$2"
                    shift
                else
                    echo "Error: Se requiere código de idioma" >&2
                    exit 1
                fi
                ;;
            *)
                echo "Opción desconocida: $1" >&2
                show_help
                exit 1
                ;;
        esac
        shift
    done

    # Execute operations in logical order
    [[ $extract -eq 1 ]] && {
        pybabel extract -F "babel.cfg" -o "${POT_FILE}" "${SRC_DIR}" && \
        echo "Mensajes extraídos a ${POT_FILE}" && \
        clean_paths_in_pot_file "${POT_FILE}"
    }
    # && procesar_archivos_traduccion "${POT_FILE}"
    
    [[ -n "$lang" ]] && mkdir -p "${LOCALE_DIR}/$lang/LC_MESSAGES" && \
        pybabel init -i "${POT_FILE}" -d "${LOCALE_DIR}" -l "$lang"
       echo "Idioma $lang inicializado"
    
    [[ $update -eq 1 ]] && pybabel update -i "${POT_FILE}" -d "${LOCALE_DIR}" && \
        echo "Archivos de traducción actualizados"
  
    [[ $compile -eq 1 ]] && pybabel compile -d "${LOCALE_DIR}" && \
        echo "Archivos de traducción compilados"
}

# Add this new function to clean paths
clean_paths_in_pot_file() {
    local pot_file="$1"
    local temp_file="${pot_file}.tmp"
    
    # Replace absolute paths with relative ones
    sed -E "s|#: .*[\\/](kiauh[\\/].*\.py):|#: \1:|g" "$pot_file" > "$temp_file" && \
    mv "$temp_file" "$pot_file"
    
    echo "Rutas limpiadas en ${pot_file}"
}

# Main execution
if [ $# -eq 0 ]; then
    show_help
    exit 0
else
    process_args "$@"
fi

# Help function
show_help() {
    echo "Uso: babel [opciones]

Script para extraer, actualizar y compilar traducciones usando Babel

Opciones:
  -h, --help          Mostrar este mensaje de ayuda
  -e, --extract       Extraer mensajes de los archivos fuente
  -u, --update        Actualizar archivos de traducción
  -c, --compile       Compilar archivos de traducción
  -l, --lang LANG     Especificar código de idioma (ej., es, fr, de)

Ejemplos:
  Extraer mensajes:
    babel --extract

  Actualizar traducciones existentes:
    babel --update

  Compilar archivos de traducción:
    babel --compile

  Inicializar nuevo idioma (ej., Español):
    babel --lang es

  Múltiples operaciones:
    babel --extract --update --compile
    babel -e -u -c"
}