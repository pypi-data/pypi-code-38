from setuptools import setup

setup(
    name='casymda',
    url='',
    author='FFC',
    author_email='fladdi.mir@gmx.de',
    packages=['casymda.BPMN', 'casymda.CoreBlocks',
              'casymda.Visualization', 'casymda.WIP'],
    install_requires=['simpy', 'xmltodict', 'Pillow'],
    version='0.1',
    zip_safe=False,
    license='MIT',
    description='A simple DES modeling and simulation environment based on simpy: create models with help of Camunda Modeler; run and debug using a 2D animation based on tkinter and PIL.',
    include_package_data=True,
    package_data={
        'casymda.Visualizer': ['state_icons/*.png']
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
)
