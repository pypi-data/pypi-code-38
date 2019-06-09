from radiant.core.toolchain import PythonRecipe
import os
import shutil

class PystacheRecipe(PythonRecipe):

    version = 'v0.5.4'
    #url = 'https://bitbucket.org/yeisoneng/django-for-android/get/{version}.tar.gz'
    # url = 'https://bitbucket.org/djangoforandroid/django-for-android/get/{version}.tar.gz'
    url = 'https://github.com/defunkt/pystache/archive/{version}.tar.gz'
    depends = ['python3crystax']


    def build_arch(self, arch):
        '''Install the Python module by calling setup.py install with
        the target Python dir.'''

        path = os.path.join(self.get_build_dir(arch.arch), 'pystache')
        os.system("2to3 --write --nobackups --no-diffs {}".format(path))

        super(PystacheRecipe, self).build_arch(arch)
        self.install_python_package(arch)
        #source, cwd


recipe = PystacheRecipe()