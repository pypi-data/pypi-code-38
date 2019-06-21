import hathorprocessing

table = 'allergies'

columns = (
    'allergyid',
    'patientunitstayid',
    'allergyoffset',
    'allergyenteredoffset',
    'allergynotetype',
    'specialtytype',
    'usertype',
    'rxincluded',
    'writtenineicu',
    'drugname',
    'allergytype',
    'allergyname',
    'drughiclseqno'
)


def read_data(chunksize=1000):
    return hathorprocessing.read_data(table, columns, chunksize)
