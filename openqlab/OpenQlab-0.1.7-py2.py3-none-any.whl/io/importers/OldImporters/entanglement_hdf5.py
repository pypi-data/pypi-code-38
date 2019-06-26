try:
    import numpy as np
    import h5py

    has_imports = True
except ImportError:
    has_imports = False


def get_importers():
    if has_imports:
        return {'entanglement_hdf5': entanglement_hdf5,
                'entanglement-hfd5': entanglement_hdf5}
    else:
        return {}


def entanglement_hdf5(file):
    """
    loads data saved by entanglement_sigpx14400 in hdf5 file format. For a
    file format definition see 
    'entanglement_sigpx14400/hdf_format_definition/fileformat.py'

    Returns:
    Two 2d arrays (data, quadratures)
    data: data[:,0]: Alice's raw data
          data[:,1]: Bob's raw data
    quadratures: quadratures[:,0]: information about which quadrature 
                                   Alice measured
                 quadratures[:,1]: information about which quadrature 
                                   Bob measured
    """
    f = h5py.File(file, "r")
    alice = np.array(f['alice']['rawdata'])
    alice_quadratures = np.array(f['alice']['quadrature'])
    bob = np.array(f['bob']['rawdata'])
    bob_quadratures = np.array(f['bob']['quadrature'])
    f.close()
    return (np.column_stack((alice, bob)),
            np.column_stack((alice_quadratures, bob_quadratures)))
