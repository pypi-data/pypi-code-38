from __future__ import print_function

from build_utils.rules.build_generic_artifact import build_generic_artifact

def build_npm_package(execution_context, artifact_name, package_dir, node_version):
    build_script = (
        """
        set -e
        apt-get update
        apt-get install -y zip
        npm install -q
        zip -rq pkg-dist.zip .
        npm test
        """
    )

    return build_generic_artifact(
        execution_context=execution_context,
        artifact_name=artifact_name,
        source_dir=package_dir,
        image='node:{0}'.format(node_version),
        build_command=build_script,
        artifact_path='pkg-dist.zip',
        artifact_extension='zip'
    )
