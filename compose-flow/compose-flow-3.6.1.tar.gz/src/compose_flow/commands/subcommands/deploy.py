import logging

from compose_flow.kube.mixins import KubeMixIn

from .base import BaseSubcommand
from .profile import Profile

ACTIONS = ['rancher', 'docker', 'rke', 'helm', 'kubectl']
PROFILE_ACTIONS = ['docker']


class Deploy(BaseSubcommand, KubeMixIn):
    """
    Subcommand for deploying an image to the docker swarm
    """
    rw_env = True
    update_version_env_vars = True

    # apply all checks to deployment
    profile_checks = Profile.get_all_checks()

    @classmethod
    def fill_subparser(cls, parser, subparser):
        subparser.add_argument('action', nargs='?', default='docker', choices=ACTIONS)

    @property
    def logger(self):
        return logging.getLogger(f'{__name__}.{self.__class__.__name__}')

    @property
    def setup_profile(self):
        if self.workflow.args.action in PROFILE_ACTIONS:
            return True
        else:
            return False

    def build_docker_command(self) -> str:
        return f"""docker stack deploy
            --prune
            --with-registry-auth
            --compose-file {self.workflow.profile.filename}
            {self.workflow.args.config_name}"""

    def build_kubectl_command(self) -> list:
        self.switch_kube_context()

        command = []

        for manifest in self.get_kubectl_manifests():
            if isinstance(manifest, str):
                manifest = {'path': manifest}
            command.append(self.get_kubectl_command(manifest))

        return command

    def build_rancher_command(self) -> list:
        self.switch_rancher_context()

        command = []

        for app in self.get_apps():
            # check if app is already installed - if so upgrade, if not install
            command.append(self.get_app_deploy_command(app))

        self.upsert_rancher_namespaces(self.workflow.args.dry_run)

        for manifest in self.get_rancher_manifests():
            if isinstance(manifest, str):
                manifest = {'path': manifest}
            command.append(self.get_kubectl_command(manifest, kubectl_prefix='rancher kubectl'))

        return command

    def build_rke_command(self) -> str:
        return self.get_rke_deploy_command()

    def build_helm_command(self) -> str:
        self.switch_kube_context()

        command = []

        for app in self.get_helm_apps():
            command.append(self.get_app_deploy_command(app, target='helm'))
        return command

    def handle(self):
        args = self.workflow.args
        env = self.workflow.environment
        action = args.action

        try:
            action_method = getattr(self, 'build_' + action + '_command')
        except AttributeError:
            self.logger.error("Unknown deployment platform: %s", action)

        command = action_method()
        command_is_list = isinstance(command, list)

        logged_command = '\n'.join(command) if command_is_list else command
        self.logger.info(logged_command)

        if not args.dry_run:
            if command_is_list:
                # If multiple commands are returned, run them one by one
                for c in command:
                    self.execute(c)
            else:
                self.execute(command)

            env.write()
