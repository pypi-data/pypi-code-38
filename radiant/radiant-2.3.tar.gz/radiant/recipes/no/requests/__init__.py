from radiant.core.toolchain import PythonRecipe

class RequestsRecipe(PythonRecipe):

    version = 'v2.18.1'
    url = 'https://github.com/kennethreitz/requests/archive/{version}.tar.gz'
    depends = ['python3crystax']

recipe = RequestsRecipe()
