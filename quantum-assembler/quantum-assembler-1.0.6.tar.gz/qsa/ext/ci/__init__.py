from subprocess import Popen, PIPE

import ioc
from qsa.ext.base import BaseExtension
from qsa.lib.datastructures import DTO

from .schema import ConfigSchema


class Extension(BaseExtension):
    name = command_name = inject = 'ci'
    schema_class = ConfigSchema
    weight = 9.0
    codebase = ioc.class_property('core:CodeRepository')
    subcommands = [
        {
            'name': 'configure',
            'args': [
                ('--origin-remote', {}),
                ('--origin-secret', {}),
                ('--origin-poll', {}),
                ('--origin-webhook', {}),
                ('--publish-registry-secret', {}),
                ('--publish-registry-url', {}),
                ('--mounted-secret', {'action': 'append', 'default': [],
                    'dest': 'mounted_secrets'}),
                ('--using', {})
            ]
        },
        {
            'name': 'notify-slack',
            'args': [
                ('--channel', {}),
                ('--channel-failed', {}),
                ('--secret', {})
            ]
        }
    ]
    nodefault = True

    def handle_notify_slack(self, args, codebase):
        self.spec.ci.notifications.slack = slack = self.quantum.get(
            'ci.notifications.slack', {})
        channels = slack.setdefault('channels', DTO())
        slack.update({
            'enabled': True,
            'channels': {
                'default': args.channel or channels.get('default'),
                'failed': args.channel_failed or channels.get('failed')
            },
            'secret': args.secret or slack.get('secret')
        })
        with self.codebase.commit("Configure Slack notifications"):
            self.quantum.update(self.spec)
            self.quantum.persist()

    def handle_configure(self, args, codebase):
        if args.using:
            with self.codebase.commit("Configure CI/CD platform", noprefix=True):
                self.spec.ci.using = args.using
                self.quantum.update(self.spec)
                self.quantum.persist(self.codebase)
        if args.origin_remote:
            with self.codebase.commit("Set origin URL for CI/CD remote sources", noprefix=True):
                self.spec.ci.origin.remote = args.origin_remote
                self.quantum.update(self.spec)
                self.quantum.persist(self.codebase)
        if args.origin_secret:
            with self.codebase.commit("Configure secret for origin pull", noprefix=True):
                self.spec.ci.origin.credentials = args.origin_secret
                self.quantum.update(self.spec)
                self.quantum.persist(self.codebase)
        if args.origin_poll:
            with self.codebase.commit("Configure poll interval for origin pull", noprefix=True):
                self.spec.ci.origin.poll = args.origin_poll
                self.quantum.update(self.spec)
                self.quantum.persist(self.codebase)
        if args.origin_webhook:
            with self.codebase.commit("Configure webhook for origin pull trigger", noprefix=True):
                self.spec.ci.origin.webhook = args.origin_webhook
                self.quantum.update(self.spec)
                self.quantum.persist(self.codebase)
        if args.publish_registry_secret:
            with self.codebase.commit("Set credential for artifact publication", noprefix=True):
                self.spec.ci.container_registries.publish.secret =\
                    args.publish_registry_secret
                self.quantum.update(self.spec)
                self.quantum.persist(self.codebase)
        if args.publish_registry_url:
            with self.codebase.commit("Set URL for artifact publication", noprefix=True):
                self.spec.ci.container_registries.publish.url =\
                    args.publish_registry_url
                self.quantum.update(self.spec)
                self.quantum.persist(self.codebase)
        if args.mounted_secrets:
            secrets = []
            with self.codebase.commit("Set mounted secrets", noprefix=True):
                for secret in args.mounted_secrets:
                    kind, name, path = str.split(secret, ':')
                    secrets.append({'name': name, 'path': path, 'kind': kind})

                self.spec.ci.mounted_secrets = secrets
                self.quantum.update(self.spec)
                self.quantum.persist(self.codebase)


    def configure(self, spec):
        if not self.spec:
            self.spec = self.schema_class.defaults()
        self.spec.ci.update(spec)
        self.quantum.update(self.spec)

    def on_autodetect(self):
        self.injector.call(self.autoconfigure)

    def autoconfigure(self, codebase):
        with self.codebase.commit("Configure remote sources"):
            args = ['git', 'config', '--get', 'remote.origin.url']
            p = Popen(args, stdout=PIPE, stdin=PIPE, stderr=PIPE)
            output, error = p.communicate()
            if p.returncode != 0:
                raise RuntimeError(output, error)
            self.spec.ci.origin.remote = str.strip(bytes.decode(output))
            self.quantum.update(self.spec)
            self.quantum.persist()

    def on_setup_makefile(self, make):
        make.setvariable('CICD_NAMESPACE', 'cicd', export=True)

    def on_pipeline_render(self, ctx):
        ctx.update({
            'USE_GITLAB': self.quantum.get('ci.origin.webhook', None) == 'gitlab',
            'USE_SLACK': 'slack' in self.quantum.get('ci.notifications', []),
            'USE_GIT': bool(self.quantum.get('ci.origin.remote')),
        })
