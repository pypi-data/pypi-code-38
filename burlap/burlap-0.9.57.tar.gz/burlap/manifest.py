"""
Tracks changes between deployments.
"""
from __future__ import print_function

from pprint import pprint
#TODO: remove? largely deprecated, use the deploy module instead

from burlap import common
from burlap.decorators import task, runs_once
from burlap import Satchel

class ManifestSatchel(Satchel):

    name = 'manifest'

    @task
    @runs_once
    def show_current(self, name):
        ret = self.get_current(name)
        print('Current manifest for %s:' % name)
        pprint(ret, indent=4)

    @task
    @runs_once
    def show_last(self, name):
        ret = self.get_last(name)
        print('Last manifest for %s:' % name)
        pprint(ret, indent=4)

    @task
    @runs_once
    def get_current(self, name):
        name = name.strip().lower()
        func = common.manifest_recorder[name]
        return func()

    @task
    @runs_once
    def get_last(self, name):
        from burlap.deploy import deploy as deploy_satchel
        name = common.assert_valid_satchel(name)
        last_thumbprint = deploy_satchel.get_previous_thumbprint()
        #print('manifest.name:', name)
        #print('manifest.last_thumbprint:')
        #pprint(last_thumbprint, indent=4)
        if last_thumbprint:
            if name in last_thumbprint:
                return last_thumbprint.get(name, type(self.genv)())
        return type(self.genv)()

    @task
    @runs_once
    def changed(self, name):
        from burlap.deploy import deploy
        name = name.strip().lower()
        if name not in common.manifest_recorder:
            print('No manifest recorder has been registered for component "%s"' % name)
        else:
            last_thumbprint = deploy.get_previous_thumbprint()
            if last_thumbprint:
                if name in last_thumbprint:
                    last_manifest = last_thumbprint[name]
                    current_manifest = common.manifest_recorder[name]()
                    if last_manifest == current_manifest:
                        print('No')
                        return False
                    print('Yes')
                    return True
                print('Yes, first deployment for this component.')
                return True
            print('Yes, first deployment.')
            return True

manifest = ManifestSatchel()
