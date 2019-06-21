import hathorprocessing

table = 'dna'

columns = (
    'instrument_name',
    'run_id',
    'flowcell_id',
    'flowcell_lane',
    'tile_number',
    'x_coord',
    'y_coord',
    'member',
    'is_filtered',
    'control_bit',
    'barcode',
    'data',
    'quality',
    'other'
)


def read_data(chunksize=1000):
    return hathorprocessing.read_data(table, columns, chunksize)
