# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['diff_1c']

package_data = \
{'': ['*']}

install_requires = \
['cjk-commons>=3.3,<4.0', 'loguru>=0.3.0,<0.4.0', 'parse-1c-build>=5.5,<6.0']

entry_points = \
{'console_scripts': ['diff1c = diff_1c.__main__:run']}

setup_kwargs = {
    'name': 'diff-1c',
    'version': '6.3.0',
    'description': 'Diff utility for 1C:Enterprise',
    'long_description': 'Утилита для сравнения *epf*-, *erf*-, *ert*- и *md*-файлов\n===\n\nЧто делает\n---\n\nФайлы разбираются с помощью пакета [parse-1c-build][1] в каталоги, которые затем сравниваются указанной в аргументах \nкомандной строки утилитой сравнения. Поддерживаются AraxisMerge, ExamDiff, KDiff3, WinMerge.\n\nПри установке пакета в каталоге скриптов интерпретатора Python создаётся исполняемый файл *diff1c.exe*.\n\nТребования\n---\n\n- Windows\n- Python 3.7 и выше. Каталоги интерпретатора и скриптов Python должны быть прописаны в переменной окружения Path\n- Пакет [parse-1c-build][1] с необходимыми настройками\n\n[1]: https://github.com/Cujoko/parse-1c-build\n',
    'author': 'Cujoko',
    'author_email': 'cujoko@gmail.com',
    'url': 'https://github.com/Cujoko/diff-1c',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
