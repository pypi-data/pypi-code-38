"""A monkey patch to zc.buildout.easy_install.develop that takes into
consideration eggs installed at both development and deployment directories."""

import os
import sys
import shutil
import tempfile
import subprocess
import pkg_resources
import zc.buildout.easy_install

from . import tools
from .envwrapper import EnvironmentWrapper

import logging
logger = logging.getLogger(__name__)

runsetup_template = """
import os
import sys
for k in %(paths)r.split(os.pathsep): sys.path.insert(0, k)
sys.path.insert(0, %(setupdir)r)

import os, setuptools

__file__ = %(__file__)r

os.chdir(%(setupdir)r)
sys.argv[0] = %(setup)r

exec(compile(open(%(setup)r).read(), %(setup)r, 'exec'))
"""

class Installer:

  def __init__(self, buildout):

    self.buildout = buildout['buildout']

    self.verbose = tools.verbose(self.buildout)

    # finally builds the environment wrapper
    self.prefixes = tools.get_prefixes(self.buildout)
    self.envwrapper = EnvironmentWrapper(logger,
        tools.debug(self.buildout),
        self.prefixes,
        buildout.get('environ', {}),
        )

    self.find_links = buildout.get('find_links', '')

  def __call__(self, spec, ws, dest, dist):
    """We will replace the default easy_install call by this one"""

    # set the environment
    self.envwrapper.set()

    # satisfy all package requirements before installing the package itself
    tools.satisfy_requirements(self.buildout, spec, ws)

    tmp = tempfile.mkdtemp(dir=dest)

    try:

        args = [sys.executable, '-c',
            zc.buildout.easy_install._easy_install_cmd, '-mZUNxd', tmp]
        if self.verbose:
            args.append('-v')
        else:
            args.append('-q')

        links = self.buildout.get('find-links', '')
        if links: args.extend(['-f', links])

        args.append(spec)

        if logger.getEffectiveLevel() <= logging.DEBUG:
            logger.debug('Running easy_install:\n"%s"\npath=%s\n',
                '" "'.join(args),
                os.pathsep.join(tools.get_pythonpath(ws, self.buildout, self.prefixes)),
                )

        sys.stdout.flush() # We want any pending output first

        exit_code = subprocess.call(list(args),
            env=dict(
              os.environ,
              PYTHONPATH=os.pathsep.join(tools.get_pythonpath(ws, self.buildout, self.prefixes)),
              ),
            )

        dists = []
        env = pkg_resources.Environment([tmp])
        for project in env:
            dists.extend(env[project])

        if exit_code:
            logger.error(
                "An error occurred when trying to install %s. "
                "Look above this message for any errors that "
                "were output by easy_install.",
                dist)

        if not dists:
            raise zc.buildout.UserError("Couldn't install: %s" % dist)

        if len(dists) > 1:
            logger.warn("Installing %s\n"
                        "caused multiple distributions to be installed:\n"
                        "%s\n",
                        dist, '\n'.join(map(str, dists)))
        else:
            d = dists[0]
            if d.project_name != dist.project_name:
                logger.warn("Installing %s\n"
                            "Caused installation of a distribution:\n"
                            "%s\n"
                            "with a different project name.",
                            dist, d)
            if d.version != dist.version:
                logger.warn("Installing %s\n"
                            "Caused installation of a distribution:\n"
                            "%s\n"
                            "with a different version.",
                            dist, d)

        result = []
        for d in dists:
            newloc = os.path.join(dest, os.path.basename(d.location))
            if os.path.exists(newloc):
                if os.path.isdir(newloc):
                    shutil.rmtree(newloc)
                else:
                    os.remove(newloc)
            os.rename(d.location, newloc)

            [d] = pkg_resources.Environment([newloc])[d.project_name]

            result.append(d)

        return result

    finally:
        shutil.rmtree(tmp)
        self.envwrapper.unset()

class Extension:

  def __init__(self, buildout):

      self.buildout = buildout['buildout']

      # shall we be verbose?
      self.verbose = tools.verbose(self.buildout)

      # replace zc.buildout's installer by our modified version, it will be
      # called indirectly by this extension, via zc.buildout
      self.installer = Installer(buildout)

  def develop(self, setup, dest, build_ext=None, executable=sys.executable):

      assert executable == sys.executable, (executable, sys.executable)
      if os.path.isdir(setup):
          directory = setup
          setup = os.path.join(directory, 'setup.py')
      else:
          directory = os.path.dirname(setup)

      working_set = tools.working_set(self.buildout)
      tools.satisfy_requirements(self.buildout, directory, working_set)

      self.installer.envwrapper.set()
      undo = []
      undo.append(self.installer.envwrapper.unset)

      try:

          if build_ext:
              setup_cfg = os.path.join(directory, 'setup.cfg')
              if os.path.exists(setup_cfg):
                  os.rename(setup_cfg, setup_cfg+'-develop-aside')
                  def restore_old_setup():
                      if os.path.exists(setup_cfg):
                          os.remove(setup_cfg)
                      os.rename(setup_cfg+'-develop-aside', setup_cfg)
                  undo.append(restore_old_setup)
              else:
                  open(setup_cfg, 'w')
                  undo.append(lambda: os.remove(setup_cfg))
              setuptools.command.setopt.edit_config(
                  setup_cfg, dict(build_ext=build_ext))

          fd, tsetup = tempfile.mkstemp()
          undo.append(lambda: os.remove(tsetup))
          undo.append(lambda: os.close(fd))

          os.write(fd, (runsetup_template % dict(
              # we reverse the order because we want the user paths to be inserted last ([::-1]).
              paths=os.pathsep.join(tools.get_pythonpath(working_set, self.buildout, self.installer.prefixes)[::-1]),
              setup=setup,
              setupdir=directory,
              __file__ = setup,
              )).encode())

          tmp3 = tempfile.mkdtemp('build', dir=dest)
          undo.append(lambda : shutil.rmtree(tmp3))

          args = [executable,  tsetup, '-q', 'develop', '-mxN', '-d', tmp3]
          if self.verbose: args[2] = '-v'

          logger.debug("in: %r\n%s", directory, ' '.join(args))

          zc.buildout.easy_install.call_subprocess(args)

          return zc.buildout.easy_install._copyeggs(tmp3, dest, '.egg-link', undo)

      finally:
          undo.reverse()
          [f() for f in undo]


def _dists_sig(dists):
    '''Override of zc.buildout.buildout._dists_sig() to avoid excessive
    directory hashing on "normal" distributions'''

    seen = set()
    result = []
    for dist in dists:
        if dist in seen:
            continue
        seen.add(dist)
        location = dist.location
        result.append(os.path.basename(location))
    return result


def extension(buildout):
    """Monkey patches zc.buildout.easy_install.develop"""

    ext = Extension(buildout)
    zc.buildout.easy_install.develop = ext.develop
    zc.buildout.easy_install.Installer._call_easy_install = ext.installer
    zc.buildout.buildout._dists_sig = _dists_sig
