import os
import unittest
from subprocess import run


class TestPackageSplitting(unittest.TestCase):

    def setUp(self):
        shlvl = int(os.getenv('CONDA_SHLVL', '0'))
        self.envs = []
        while shlvl > 0:
            self.envs.append(os.getenv('CONDA_DEFAULT_ENV'))
            # TODO proper way to call conda commands
            run('bash -i -c "conda deactivate"', shell=True)
            shlvl = int(os.getenv('CONDA_SHLVL', '0'))

    def tearDown(self):
        for env in self.envs:
            run(f'bash -i -c "conda activate {env}"', shell=True)

    def test_get_base_prefix(self):
        run('bash -i -c "conda activate"', shell=True)

        shlvl = int(os.getenv('CONDA_SHLVL', '0'))
        self.assertEqual(shlvl, 0)

        prefix = os.getenv('CONDA_PREFIX')
        # assert: prefix == base environment *path*

        default_env = os.getenv('CONDA_DEFAULT_ENV')
        self.assertEqual(default_env, 'base')

    def test_get_active_prefix(self):
        raise NotImplementedError()

    def test_get_installed_packages(self):
        raise NotImplementedError()

    def test_get_channels(self):
        raise NotImplementedError()


if __name__ == '__main__':
    unittest.main()
