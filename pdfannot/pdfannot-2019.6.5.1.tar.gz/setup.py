from setuptools import setup, find_packages
import pdfannot

setup(name="pdfannot",
      install_requires=['pandas', 'pymupdf', 'xlrd'],
      version=pdfannot.__version__,
      description='PDF Annotation Utils',
      author='Arthur RENAUD ; Antoine MARULLAZ => Stackadoc',
      author_email='arthur.b.renaud@gmail.com',
      url='https://bitbucket.org/ArthurRenaud/pdfannot/',
      packages=find_packages(),
      tests_require=["pytest"],
      python_requires='>=3.5',
      setup_requires=["pytest-runner"],
      long_description=open('README.md').read(), long_description_content_type="text/markdown",

      # Active la prise en compte du fichier MANIFEST.in
      include_package_data=True,

      package_data={'': ['pdfannot/test_ressources/pdf_without_annot.pdf']},
      classifiers=[
            "Programming Language :: Python",
            "Development Status :: 1 - Planning",
            "License :: OSI Approved",
            "Natural Language :: French",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3.6",
            "Topic :: Communications",
      ],

      )

