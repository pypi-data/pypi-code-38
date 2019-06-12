import setuptools
from lgblkb_tools.global_support import ConfigReader
from lgblkb_tools.log_support import create_logger,with_logging
from lgblkb_tools.folder_utils import Folder
import ruamel.yaml as raml

simple_logger=create_logger('setup_logs')

with open("README.md","r") as fh:
	long_description=fh.read()

def get_update_version(info_filepath):
	# yaml.dump(dict(version='0.0.8'),open(info_filepath,'w'))
	info_data=ConfigReader(info_filepath)
	current_version=[int(x) for x in info_data.version.obj.split('.')]
	current_version[-1]+=1
	info_data['version']='.'.join(map(str,current_version))
	return info_data

install_requires=[
	'pandas',
	'python_log_indenter',
	'celery',
	'numpy',
	'geojson',
	'python_dateutil',
	'ruamel.yaml',
	'sklearn',
	'geojsonio',
	'matplotlib',
	'pyproj',
	'Shapely',
	'geojson',
	'scikit_learn',
	'more_itertools',
	'requests',
	'docker',
	'python-box',
	'sqlalchemy',
	'geoalchemy2',
	'psycopg2',
	'colorlog',
	'python-telegram-bot',
	'jsonpickle',
	'fabric',
	'circus',
	'checksumdir',
	'joblib',
	]

@simple_logger.with_logging()
def setup(version):
	setuptools.setup(
		name="lgblkb_tools",
		version=version,
		author="Dias Bakhtiyarov",
		author_email="dbakhtiyarov@nu.edu.kz",
		description="Some useful tools for everyday routine coding improvisation)",
		long_description=long_description,
		long_description_content_type="text/markdown",
		url="https://bitbucket.org/lgblkb/lgblkb_tools",
		packages=setuptools.find_packages(),
		classifiers=(
			"Programming Language :: Python :: 3.6",
			"License :: OSI Approved :: MIT License",
			"Operating System :: OS Independent",
			),
		install_requires=install_requires
		)

@simple_logger.with_logging()
def main():
	# yaml=raml.YAML()
	# yaml.default_flow_style=False
	# yaml.dump(dict(version='1.1.2'),open(r'package_info.yaml','w'))
	# return
	base_dir=Folder(r'/home/lgblkb/PycharmProjects/lgblkb_tools/')
	build_dir=base_dir.create('build')
	dist_dir=base_dir.create('dist')
	info_filepath=r'/home/lgblkb/PycharmProjects/lgblkb_tools/package_info.yaml'
	info_data=get_update_version(info_filepath)
	simple_logger.info('New version: %s',info_data.version.obj)
	build_dir.delete()
	dist_dir.delete()
	setup(info_data.version.obj)
	info_data.update()
	pass

if __name__=='__main__':
	#
	simple_logger.get_filepath(ext='log',include_depth=0).add_handler()
	main()
	pass
