from __future__ import print_function

import os
import posixpath
from xml.etree import ElementTree

from build_utils.rules.build_generic_artifact import build_generic_artifact

def build_maven_artifact(execution_context, artifact_name, project_dir):
    # Get project name and version from POM file
    full_project_dir = os.path.join(execution_context.dir_path, project_dir)
    pom_file_path = os.path.join(full_project_dir, 'pom.xml')
    pom_tree = ElementTree.parse(pom_file_path)
    pom_ns = {
        'mvn': 'http://maven.apache.org/POM/4.0.0'
    }
    pom_name = pom_tree.find('./mvn:name', pom_ns).text
    pom_version = pom_tree.find('./mvn:version', pom_ns).text

    jar_file_name = '{0}-{1}.jar'.format(pom_name, pom_version)

    return build_generic_artifact(
        execution_context=execution_context,
        artifact_name=artifact_name,
        source_dir=project_dir,
        image='maven:3.5',
        build_command='mvn clean install',
        artifact_path=posixpath.join('target', jar_file_name),
        artifact_extension='jar'
    )
