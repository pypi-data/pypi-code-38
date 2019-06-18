import setuptools

setuptools.setup(
        name='dlw',
        version='0.0.1',
        author='Julia Chmyz',
        author_email='julia@chmyz.com',
        packages=setuptools.find_packages(),
        include_package_data=True,
        url='https://github.com/jchmyz/DoublyLabeledWater',
        license='LICENSE.txt',
        description='Open source web app to conduct doubly labeled water study calculations.',
        long_description=open('README.md').read(),
        install_requires=[
            "numpy",
            "python-csv",
            "flask",
            "flask-restful"
        ],
        entry_points={"console_scripts": {"run-dlw = dlw.web.app:run_app"}}
)
