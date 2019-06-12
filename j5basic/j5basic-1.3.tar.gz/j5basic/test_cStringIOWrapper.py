from j5basic import cStringIOWrapper

def test_wrapper():
    myio = cStringIOWrapper.StringIO()
    myio.write('Testing\n')
    myio.writelines(['This\n', 'Class\n'])
    myio.flush()
    myio.close()