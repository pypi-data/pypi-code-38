from pysb.builder import Builder
try:
    import trum
    from truml.readers import KappaReader
    import pyparsing as pp
except ImportError:
    KappaReader = None
    pp = None
import io

class KappaImportError(Exception):
    pass


class KappaBuilder(Builder):
    """
    Assemble a Model from a .ka file.

    See :py:func:`model_from_kappa` for further details.
    """
    def __init__(self, filename, force=False, cleanup=True):
        super(KappaBuilder, self).__init__()
        if KappaReader is None:
            raise ImportError('TRuML is needed (e.g. pip install truml)')
        kr = KappaReader(filename)
        try:
            model = kr.parse()
        except pp.ParseException as pe:
            raise KappaImportError(pe)

        out = io.StringIO
        model.write_as_bngl(out, False)
        print(out)
        raise


def model_from_kappa(filename, force=False, cleanup=True):
    """
    Convert a BioNetGen .bngl model file into a PySB Model.

    Notes
    -----

    The following features are not supported in PySB and will cause an error
    if present in a .bngl file:

    * Fixed species (with a ``$`` prefix, like ``$Null``)
    * BNG excluded or included reaction patterns (deprecated in BNG)
    * BNG local functions
    * Molecules with identically named sites, such as ``M(l,l)``
    * BNG's custom rate law functions, such as ``MM`` and ``Sat``
      (deprecated in BNG)

    Parameters
    ----------
    filename : string
        A BioNetGen .bngl file
    force : bool, optional
        The default, False, will raise an Exception if there are any errors
        importing the model to PySB, e.g. due to unsupported features.
        Setting to True will attempt to ignore any import errors, which may
        lead to a model that only poorly represents the original. Use at own
        risk!
    cleanup : bool
        Delete temporary directory on completion if True. Set to False for
        debugging purposes.
    """
    bb = KappaBuilder(filename, force=force, cleanup=cleanup)
    return bb.model
