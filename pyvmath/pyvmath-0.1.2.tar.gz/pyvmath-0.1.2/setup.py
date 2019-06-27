from distutils.core import setup, Extension

sfc_module = Extension('pyvmath', sources=['pyVectorMath.cpp'])

setup(name='pyvmath', version='0.1.2',
		author=u'Kiharu Shishikura',
		author_email='shishi@indigames.net',
		description='C++ extension Vector Mathematics Package for 3D and 2D games.',
		ext_modules=[sfc_module],
		long_description=open('README.md').read(),
		license='MIT',
		classifiers=[
			'Intended Audience :: Developers',
			'License :: OSI Approved :: MIT License',
			'Programming Language :: Python :: 3',
			'Operating System :: MacOS :: MacOS X',
			'Operating System :: POSIX :: Linux',
			'Operating System :: Microsoft :: Windows',
			'Topic :: Games/Entertainment',
		],
      )
