# Copyright (c) 2018. Uniquid Inc. or its affiliates. All Rights Reserved.
#
# License is in the "LICENSE" file accompanying this file.
# See the License for the specific language governing permissions and limitations under the License.

import click


def print_error(in_string):
    """Print a string to stderr using click framework. Provides a platform
    independant way of printing to stderr to the core code.

        Arguments:
        in_string -- String.
    """
    click.echo(message=in_string, err=True)
