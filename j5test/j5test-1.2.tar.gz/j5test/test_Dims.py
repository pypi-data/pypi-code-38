from j5test import ArrayDim, BrowserDim, DictDim

def test_array_dim():
    array_dim = ArrayDim.ArrayDim(['A', 'B', 'C'])
    browser_dim = BrowserDim.BrowserDim()
    dict_dim = DictDim.DictDim({'A': 1, 'B': 2, 'C': 3})
