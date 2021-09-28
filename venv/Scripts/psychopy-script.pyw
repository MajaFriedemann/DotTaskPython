#!C:\Users\majaf\PycharmProjects\ConfidenceMatchingEEG\venv\Scripts\pythonw.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'PsychoPy==2021.2.0','gui_scripts','psychopy'
__requires__ = 'PsychoPy==2021.2.0'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('PsychoPy==2021.2.0', 'gui_scripts', 'psychopy')()
    )
