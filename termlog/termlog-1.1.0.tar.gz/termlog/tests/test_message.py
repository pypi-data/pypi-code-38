

def test_multiline_echo():
    from termlog import echo

    message = 'hi'

    echo(
        f'{message}'
        )
