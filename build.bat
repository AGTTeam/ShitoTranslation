pipenv run pyinstaller --clean --icon=icon.ico --add-binary "xdelta.exe;." --exclude-module="numpy" --distpath . -F --hidden-import="pkg_resources.py2_warn" tool.py
