import locale
import os
from pathlib import Path
from babel.support import Translations

# Configurar Babel
localedir: str = os.path.join(Path(__file__).parent.parent, 'locale')
lang: str = locale.getdefaultlocale()[0] or 'en'

# Cargar traducciones con gettext
try:
    trans = Translations.load(localedir, locales=[lang])
except FileNotFoundError:
    trans = Translations.load(localedir, locales=['en'])

# Crear el alias _ para la función de traducción
_ = trans.gettext