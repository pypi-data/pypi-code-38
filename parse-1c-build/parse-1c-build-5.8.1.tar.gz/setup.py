# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['parse_1c_build']

package_data = \
{'': ['*']}

install_requires = \
['cjk-commons>=3.3,<4.0', 'commons-1c>=3.1,<4.0']

entry_points = \
{'console_scripts': ['p1cb = parse_1c_build.__main__:run']}

setup_kwargs = {
    'name': 'parse-1c-build',
    'version': '5.8.1',
    'description': 'Parse and build utilities for 1C:Enterprise',
    'long_description': 'Утилита для разборки и сборки *epf*-, *erf*-, *ert*- и *md*-файлов\n===\n\nЧто делает\n---\n\nПри установке пакета в каталоге скриптов интерпретатора Python создаётся исполняемый файл *p1cb.exe*. Его можно \nзапустить с командой *parse* для разборки *epf*- и *erf*-файлов с помощью [V8Reader][1] или V8Unpack, *ert*- и \n*md*-файлов с помощью [GComp][2], или с командой *build* для сборки *epf*- и *erf*-файлов с помощью V8Unpack, *ert*- и \n*md*-файлов с помощью [GComp][2].\n\nПути к сервисной информационной базе, *V8Reader.epf*, *V8Unpack.exe* и GComp указываются в файле настроек \n*settings.yaml*, который сначала ищется в текущем каталоге, затем в каталоге данных приложения пользователя \n(в Windows 10 каталог *C:\\Users\\\\<Пользователь>\\AppData\\Roaming\\util-1c\\parse-1c-build\\>*), а затем в общем каталоге \nданных приложения (в Windows 10 каталог *C:\\ProgramData\\util-1c\\parse-1c-build\\>*). Если путь к платформе \n1С:Предприятие 8 в файле настроек не указан, то он ищется автоматически.\n\nТребования\n---\n\n- Windows\n- Python 3.7 и выше. Каталоги интерпретатора и скриптов Python должны быть прописаны в переменной окружения Path\n- Платформа 1С:Предприятие 8.3\n- Сервисная информационная база (в которой будет запускаться *V8Reader.epf*)\n- [V8Reader][1]\n- V8Unpack\n- [GComp][2]\n\n[1]: https://github.com/xDrivenDevelopment/v8Reader\n[2]: http://1c.alterplast.ru/gcomp/\n',
    'author': 'Cujoko',
    'author_email': 'cujoko@gmail.com',
    'url': 'https://github.com/Cujoko/parse-1c-build',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
