from radiant.core.toolchain import PythonRecipe

class DjangoRecipe(PythonRecipe):

    version = '2.0'
    url = 'https://github.com/django/django/archive/{version}.tar.gz'
    depends = ['python3crystax']

recipe = DjangoRecipe()
