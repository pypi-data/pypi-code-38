from setuptools import setup, find_packages

# Clasificadores: https://pypi.org/pypi?%3Aaction=list_classifiers

def get_readme():
    readme_txt = ""
    try:
        readme_txt = open('README.md').read()
    except Exception as e:
        print("Ha ocurrido un inconveniente: " + str(e))
    return readme_txt

setup(
    name = 'simono-especificaciones',
    version='0.0.14',
    author = 'Ecom Developers',
    author_email = 'simono@ecom.com.ar',
    description=('Especificaciones de Sensores para Sistema de Monitoreo de Nodos'),
    long_description=get_readme(),
    license='BSD',
    keywords='simono iot raspberry',
    url = 'https://bitbucket.org/lucasecom/especificaciones_simono/src',
    packages=['simono_especificaciones', 'simono_especificaciones.especificaciones', 'simono_especificaciones.raspbian', 'simono_especificaciones.sensores', 'simono_especificaciones.sensores.raspberry', 'simono_especificaciones.web'],
    #packages=find_packages(),
    package_data={
        #'starwars_ipsum': ['*.txt']
    },
    install_requires=[],
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities',
    ]
)



