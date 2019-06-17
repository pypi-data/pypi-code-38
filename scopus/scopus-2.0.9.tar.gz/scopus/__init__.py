from pbr.version import VersionInfo

_v = VersionInfo('scopus').semantic_version()
__version__ = _v.release_string()
version_info = _v.version_tuple()

text = "package scopus has been renamed to pybliometrics.  Please see "\
       "https://pybliometrics.readthedocs.io/en/stable/tips.html#"\
       "migration-guide-from-scopus-to-pybliometrics for a migration guide."
raise DeprecationWarning(text)
