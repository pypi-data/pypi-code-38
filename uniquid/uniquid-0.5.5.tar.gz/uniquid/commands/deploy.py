# Copyright (c) 2018. Uniquid Inc. or its affiliates. All Rights Reserved.
#
# License is in the "LICENSE" file accompanying this file.
# See the License for the specific language governing permissions and limitations under the License.

import click
from uniquid.core.login_manager import LoginManager
from uniquid.core.cli_console import CliConsole
from uniquid.core.deploy import Deploy
import uniquid.commands.common as common


@click.command(name='deploy')
@click.argument('platform',
                nargs=1,
                required=True)
@click.option('--yes', '-y',
              is_flag=True,
              help=('Automatic deployment. Answer yes to all questions during the deployment.'),
              required=False)
def deploy(platform, yes):
    """Deploy UniquID security and integration components to platform PLATFORM.

        Supported platforms: basic, aws

        Automatic deployment (--yes) can normally be used without any problems.
        A list of the newly created cloud resources is printed at the end
        of the deployment of the components.

        Once the deployment has terminated successfully, the TIMESTAMP
        identifier which is printed will uniquely identify the AWS Resources
        which were created and deployed.
    """
    cc = CliConsole(click.echo, common.print_error,
                    'text', click.ClickException,
                    click.confirm, click.prompt)
    lm = LoginManager(cc)
    deploy = Deploy(cc, lm)
    deploy.deploy(in_platform=platform, in_yesmode=yes)
    cc.happy_exit()


@click.command(name='undeploy')
@click.argument('platform',
                nargs=1,
                required=True)
@click.argument('timestamps',
                nargs=-1,
                required=False)
@click.option('--yes', '-y',
              is_flag=True,
              help=('Automatic undeployment. Answer yes to all questions during the removal of the components.'),
              required=False)
def undeploy(platform, timestamps, yes):
    """Remove UniquID security components from platform PLATFORM. TIMESTAMPS is
       a space-separated list of one or more of the timestamps of any deployed
       components which should be removed.

        Supported platforms: aws

        Automatic undeployment (--yes) can normally be used without any problems.
    """
    cc = CliConsole(click.echo, common.print_error,
                    'text', click.ClickException,
                    click.confirm, click.prompt)
    lm = LoginManager(cc)
    deploy = Deploy(cc, lm)
    deploy.undeploy(in_platform=platform, in_timestamps=timestamps, in_yesmode=yes)
    cc.happy_exit()
