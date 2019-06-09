from radiant.core.toolchain import PythonRecipe

class QuickapiRecipe(PythonRecipe):

    version = 'tip'
    url = 'https://bitbucket.org/yeisoneng/python-quickapi/get/{version}.tar.gz'
    depends = ['python3crystax']

recipe = QuickapiRecipe()
