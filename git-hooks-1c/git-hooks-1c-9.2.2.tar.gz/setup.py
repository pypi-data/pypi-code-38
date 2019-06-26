# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['git_hooks_1c']

package_data = \
{'': ['*']}

install_requires = \
['cjk-commons>=3.3,<4.0', 'fleep>=1.0,<2.0', 'parse-1c-build>=5.5,<6.0']

entry_points = \
{'console_scripts': ['gh1c = git_hooks_1c.__main__:run']}

setup_kwargs = {
    'name': 'git-hooks-1c',
    'version': '9.2.2',
    'description': 'Git hooks utilities for 1C:Enterprise',
    'long_description': 'Набор утилит для перехватчиков (hooks) Git для работы с 1С\n===\n\nЧто делает\n---\n\nПри установке пакета в каталоге скриптов интерпретатора Python создаётся исполняемый файл *gh1c.exe*. Смотри список \nподдерживаемых команд в составе.\n\nТребования\n---\n\n- Windows\n- Python 3.7 и выше. Каталоги интерпретатора и скриптов Python должны быть прописаны в переменной окружения Path\n- Пакеты virtualenv и virtualenvwrapper-win\n- Пакет [parse-1c-build][1] с необходимыми настройками\n\nСостав\n---\n\n- *install.py* — скрипт, создающий хуки в *.git/hooks* проекта. Запускается командой *install*.\n- *uninstall.py* — скрипт, удаляющий хуки из *.git/hooks* проекта. Запускается командой *uninstall*.\n- *pre-commit.sample* — образец hook-скрипта, запускающего *pre-commit-1c.bat*\n- *pre_commit.py* — скрипт для разборки *epf*-, *erf*-, *ert*- и *md*-файлов с помощью пакета \n[parse-1c-build][1] в каталоги, которые затем добавляются в индекс и помещаются в git-репозиторий. Запускается командой \n*pre_commit*.\n\n[1]: https://github.com/Cujoko/parse-1c-build\n',
    'author': 'Cujoko',
    'author_email': 'cujoko@gmail.com',
    'url': 'https://github.com/Cujoko/git-hooks-1c',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
