from radiant.core.toolchain import PythonRecipe

class DjangoStaticPrecompilerRecipe(PythonRecipe):

    version = '1.7'
    url = 'https://github.com/andreyfedoseev/django-static-precompiler/archive/{version}.tar.gz'
    depends = ['python3crystax', 'django']

recipe = DjangoStaticPrecompilerRecipe()
