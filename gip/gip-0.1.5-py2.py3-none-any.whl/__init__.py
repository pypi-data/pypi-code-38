import pbr.version

version_info = pbr.version.VersionInfo('gip')
__version__ = version_info.release_string()
