# THIS FILE IS GENERATED FROM PADDLEPADDLE SETUP.PY
#
full_version    = '1.5.0'
major           = '1'
minor           = '5'
patch           = '0'
rc              = '0'
istaged         = False
commit          = '401c03fc20478f5cc067440422fc3a7b306d0e32'
with_mkl        = 'ON'

def show():
    if istaged:
        print('full_version:', full_version)
        print('major:', major)
        print('minor:', minor)
        print('patch:', patch)
        print('rc:', rc)
    else:
        print('commit:', commit)

def mkl():
    return with_mkl
