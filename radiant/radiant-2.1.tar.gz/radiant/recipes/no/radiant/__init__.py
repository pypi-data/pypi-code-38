from radiant.core.toolchain import PythonRecipe
import os
import shutil

class RadiantRecipe(PythonRecipe):

    version = 'tip'
    #url = 'https://bitbucket.org/yeisoneng/django-for-android/get/{version}.tar.gz'
    url = 'https://bitbucket.org/radiantforandroid/radiantframework/get/{version}.tar.gz'
    depends = ['python3crystax']

    def build_arch(self, arch):
        '''Install the Python module by calling setup.py install with
        the target Python dir.'''

        #shutil.rmtree(os.path.join(self.get_build_dir(arch.arch), 'radiant', 'builder'), ignore_errors=True)
        shutil.rmtree(os.path.join(self.get_build_dir(arch.arch), 'radiant', 'core'), ignore_errors=True)
        #shutil.rmtree(os.path.join(self.get_build_dir(arch.arch), 'radiant', 'frammework'), ignore_errors=True)
        shutil.rmtree(os.path.join(self.get_build_dir(arch.arch), 'radiant', 'projects'), ignore_errors=True)
        shutil.rmtree(os.path.join(self.get_build_dir(arch.arch), 'radiant', 'recipes'), ignore_errors=True)
        shutil.rmtree(os.path.join(self.get_build_dir(arch.arch), 'radiant', 'src'), ignore_errors=True)

        super(RadiantRecipe, self).build_arch(arch)
        self.install_python_package(arch)
        #source, cwd


recipe = RadiantRecipe()