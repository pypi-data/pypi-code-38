from __future__ import print_function
import os
import sys
from argparse import ArgumentParser

entry_point_contents = '''#!/bin/bash -eu

export PYTHONPATH="${{PYTHONPATH:+$PYTHONPATH:}}{tool_path}"

# Add your configuration here:
# ...

# Tool start:
exec {executable} -m qmenta.sdk.executor "$@"
'''


def main():
    parser = ArgumentParser()
    parser.add_argument('target')
    parser.add_argument('tool_paths', nargs='+')
    parser.add_argument("--example-tool-path",
                        help="the directory should be included in tool_paths")
    parser.add_argument('--example-tool-type', choices=tool_types)

    options = parser.parse_args()

    make_entrypoint(options.target, options.tool_paths,
                    options.example_tool_path, options.example_tool_type)


# Default tools
matlab_default_tool = """

import os

def run(context):
    # Get information from the platform such as patient name, user_id, ssid...
    analysis_data = context.fetch_analysis_data()
    # example_string = 'Analysis name: ' + analysis_data['name'] + '\n'

    # Get the complete list of input file handlers matching the requirements
    input_files = context.get_files('input', modality='T1')

    # Download all those files
    for file_handler in input_files:
        file_handler.download('/root/')  # Keeping the original names

        # Call the MATLAB helper script with the path of the MATLAB runtime installation
        # Make sure your script finalizes. Otherwise this call will be waiting forever
        # Alternatively, you can always implement a timeout (e.g. with subprocess)

        # os.system('/root/MATLAB_run_script.sh /opt/mcr/v92')

        # Last, upload the results to the platform
        # context.upload_file('/root/results.png', 'results.png')
"""

minimal_default_tool = """
def run(context):
    # Get information from the platform such as patient name, user_id, ssid...
    analysis_data = context.fetch_analysis_data()

    # Get the complete list of input file handlers
    input_files = context.get_files('input')  # You can add fitlers (modality, tags...)

    # Download them
    for file_handler in input_files:
        file_handler.download('/root/')

        # Do some processing here
        # ...

        # And upload the results
        # context.upload_file(path, path_in_output)  # You can add filters (modality, tags...)
"""

mrinfo_mrtrix_default_tool = """
import os

def run(context):
    # Get information from the platform such as patient name, user_id, ssid...
    analysis_data = context.fetch_analysis_data()

    with open('/root/sizes.txt', 'w') as fp:
        fp.write('Analysis name: ' + analysis_data['name'] + '\n')

    # Get the complete list of files
    input_files = context.get_files('input', modality='T1')

    # Do some processing (run mrinfo for every file)
    for f in input_files:
        f.download('/root/')
        os.system('mrinfo {} >> /root/sizes.txt'.format(f.get_file_path()))

    # Last, upload the results to the platform
    context.upload_file('/root/sizes.txt', 'mrinfo_outputs.txt')
"""

tool_types = {
    "minimal": minimal_default_tool,
    "matlab": matlab_default_tool,
    "mrtrix": mrinfo_mrtrix_default_tool,
}


def make_entrypoint(target, tool_paths, example_tool_path, example_tool_type, help_stream=sys.stderr):
    if not example_tool_path.endswith(".py"):
        raise RuntimeError(
            "expected tool path to be a python file to be created")

    with open(target, 'w') as fp:
        fp.write(entry_point_contents.format(
            executable=sys.executable,
            tool_path=":".join(tool_paths)
        ))

    if example_tool_path:
        with open(example_tool_path, 'w') as fp:
            fp.write(tool_types.get(example_tool_type, "minimal"))

        print("execute:", file=help_stream)
        print("$", target, os.path.basename(example_tool_path)[:-len('.py')] + ":run", file=help_stream)
        print("to run the example tool", file=help_stream)


if __name__ == '__main__':
    main()
