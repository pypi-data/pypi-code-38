from setuptools import setup, find_packages

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
        name='bwscan',
        version='0.1',
        packages=find_packages(),
        license='Proprietary',
        description=readme(),
        classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 3.4',
        'Topic :: Environment :: Other Environment'
        ],     
        keywords='bwscan',
        url='https://github.com/zimmerst/bwscan.git',
        author='Stephan Zimmer on behalf of BestWestern Scandinavia',
        author_email='stephan.zimmer@bestwestern.se',
        install_requires=['requests','pyyaml','o365','pytesseract','pdf2image','tqdm','sqlalchemy','pymysql'],

        entry_points={
            'console_scripts': [
                'faxocr-daemon=bwscan.daemons.server.fax_ocr_unattended:main'
            ]
        }
)
  
 
