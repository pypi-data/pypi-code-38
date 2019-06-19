from tormor.dsn import makeDSN

def test_make_dsn():
    opts = {
        '-h': 'localhost',
        '-d': 'tormordb',
        '-U': 'tormor',
        '-p': '8000',
        '-P': 'tormor'
    }
    expected_dsn = "postgresql://tormor:tormor@localhost:8000/tormordb"
    assert makeDSN(opts) == expected_dsn