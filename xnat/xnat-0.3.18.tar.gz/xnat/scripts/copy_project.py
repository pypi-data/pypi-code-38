#!/usr/bin/env python
import argparse
import os
import tempfile
import shutil

import six
from six.moves import html_parser

import xnat


class XNATProjectCopier:
    def __init__(self, source_xnat, source_project, dest_xnat, dest_project):
        self.source_xnat = source_xnat
        self.source_project = source_project
        self.dest_xnat = dest_xnat
        self.dest_project = dest_project
        self.temp_dir = tempfile.mkdtemp()
        print('Using tmpdir: {}'.format(self.temp_dir))

    def __del__(self):
        shutil.rmtree(self.temp_dir)
        pass

    def copy_fields(self, source, destination, prefix=''):
        for field_id, value in source.fields.items():
            # Avoid double escaping of html chars
            destination.fields[field_id] = html_parser.HTMLParser().unescape(value)
            print('{prefix}copying field: {}'.format(
                field_id, prefix=prefix
            ))

    def copy_demographics(self, source_subject, dest_subject):
        """
        Copy over all demographics for a subject
        """
        print('  copying demographics')
        demographic_list = [
            'age', 'birth_weight', 'dob', 'education', 'education_desc', 'employment',
            'ethnicity', 'gender', 'gestational_age', 'handedness', 'height', 'post_menstrual_age',
            'race', 'race2', 'race3', 'race4', 'race5', 'race6', 'ses', 'weight', 'yob']

        demographics_data = {}

        for demographic in demographic_list:
            value = source_subject.demographics.data.get(demographic)
            if value is not None:
                demographics_data[demographic] = value

        dest_subject.demographics.mset(demographics_data)

    def copy_resource(self, source_resource, dest_resource, prefix=''):
        # Download resource content, and upload it again
        print('{prefix}copying resource {}'.format(source_resource.label, prefix=prefix))

        source_resource.download_dir(self.temp_dir, verbose=False)
        for path, dirnames, filenames in os.walk(self.temp_dir):
            if source_resource.label in dirnames and os.path.split(path)[-1] == 'resources':
                resource_path = os.path.join(path, source_resource.label, 'files')
                if os.path.exists(resource_path):
                    break
        else:
            raise ValueError('Could not find directory for downloaded resource!')

        # Upload entire resource directory
        dest_resource.upload_dir(resource_path, method='tgz_memory')

    def copy_resources(self, source_object, dest_object, prefix=''):
        for source_resource in source_object.resources.values():
            resource_id = source_resource.label
            if resource_id in dest_object.resources:
                print('{}Skipping resource {}'.format(prefix, resource_id))
                # Already there, do not copy
                continue

            # Create a resources of the same xsitype
            print('{}Copying resource {}'.format(prefix, resource_id))
            dest_class = self.dest_xnat.XNAT_CLASS_LOOKUP[source_resource.__xsi_type__]
            dest_resource = dest_class(
                parent=dest_object,
                label=source_resource.label,
                content=source_resource.content
            )

            # Copy resource file contents
            if len(source_resource.files) > 0:
                self.copy_resource(source_resource, dest_resource, prefix=prefix)

    def copy_experiment(self, source_experiment, dest_experiment):
        self.copy_fields(source_experiment, dest_experiment, prefix='    ')
        self.copy_resources(source_experiment, dest_experiment, prefix='    ')

        for scan in source_experiment.scans.values():
            print('    copying scan {} / {}'.format(scan.id, scan.type))
            if scan.id not in dest_experiment.scans:
                dest_class = self.dest_xnat.XNAT_CLASS_LOOKUP.get(scan.__xsi_type__)
                if dest_class is None:
                    print('     [WARNING] {} class not found on destination server, skipping'.format(source_experiment.__xsi_type__))
                    continue

                print('     creating scan {}'.format(scan.id))
                dest_scan = dest_class(parent=dest_experiment, id=scan.id, type=scan.type)
            else:
                dest_scan = dest_experiment.scans[scan.id]

            self.copy_resources(scan, dest_scan, prefix='     ')

        for assessor_id, source_assessor in source_experiment.assessors.items():
            # Create an assessor of the same xsitype
            if source_assessor.__xsi_type__ != 'xnat:mrAssessorData':
                dest_class = self.dest_xnat.XNAT_CLASS_LOOKUP[source_assessor.__xsi_type__]
            else:
                print("    Avoiding creation of invalid class xnat:mrAssessorData,"
                      " substituting with xnat:qcAssessmentData")
                dest_class = self.dest_xnat.classes.QcAssessmentData
            dest_assessor = dest_class(parent=dest_experiment, label=source_assessor.label)
            print('    copying assessor {}'.format(source_assessor.label))
            self.copy_resources(source_assessor, dest_assessor, prefix='      ')

    def copy_subject(self, source_subject, dest_subject):
        self.copy_demographics(source_subject, dest_subject)
        self.copy_fields(source_subject, dest_subject, prefix='  ')
        self.copy_resources(source_subject, dest_subject, prefix='  ')

        for source_experiment in source_subject.experiments.values():
            print('  copying experiment  {}'.format(source_experiment.label))

            if hasattr(source_experiment, 'scans') and len(source_experiment.scans) > 0:
                print('    copying data')
                temp_file = os.path.join(self.temp_dir, source_experiment.label + '.zip')
                try:
                    source_experiment.download(temp_file, verbose=False)
                    try:
                        dest_experiment = self.dest_xnat.services.import_(
                            temp_file,
                            project=self.dest_project.id,
                            subject=source_experiment.subject.label,
                            experiment=source_experiment.label
                        )
                    except xnat.exceptions.XNATUploadError as exception:
                        print('    [ WARNING] Experiment did not include parsable dicom files, creating empty experiment')
                        if 'not include parseable files' in exception.args[0]:
                            dest_class = self.dest_xnat.XNAT_CLASS_LOOKUP.get(source_experiment.__xsi_type__)
                            if dest_class is None:
                                print('    [WARNING] {} class not found on destination server, skipping'.format(source_experiment.__xsi_type__))
                                continue

                            dest_experiment = dest_class(parent=dest_subject, label=source_experiment.label)
                        else:
                            raise
                finally:
                    try:
                        os.remove(temp_file)
                    except:
                        pass  # Allowed

            else:
                print('    creating empty experiment')
                dest_class = self.dest_xnat.XNAT_CLASS_LOOKUP.get(source_experiment.__xsi_type__)
                if dest_class is None:
                    print('    [WARNING] {} class not found on destination server, skipping'.format(source_experiment.__xsi_type__))
                    continue

                dest_experiment = dest_class(parent=dest_subject, label=source_experiment.label)
            self.copy_experiment(source_experiment, dest_experiment)

    def copy_project(self):
        source_project = self.source_project
        dest_project = self.dest_project

        print('Copying fields')
        self.copy_fields(source_project, dest_project)
        print('Copying resources')
        self.copy_resources(source_project, dest_project, prefix='  ')

        for subject_id, source_subject in self.source_project.subjects.items():
            print('copying subject {}'.format(source_subject.label))
            dest_subject = self.dest_xnat.classes.SubjectData(parent=self.dest_project, label=source_subject.label)
            self.copy_subject(source_subject, dest_subject)

    def start(self):
        self.copy_project()


def main():
    parser = argparse.ArgumentParser(description='Copy Xnat projects')
    parser.add_argument('--source-host', type=six.text_type, required=True, help='source XNAT url')
    parser.add_argument('--source-project', type=six.text_type, required=True, help='source XNAT project')
    parser.add_argument('--dest-host', type=six.text_type, required=True, help='destination XNAT url')
    parser.add_argument('--dest-project', type=six.text_type, required=True, help='destination XNAT project')
    args = parser.parse_args()

    with xnat.connect(args.source_host) as source_xnat, xnat.connect(args.dest_host) as dest_xnat:
        # Find projects
        try:
            source_project = source_xnat.projects[args.source_project]
            dest_project = dest_xnat.projects[args.dest_project]
        except KeyError as error:
            print(error.message)
        else:
            # Create and start copier
            copier = XNATProjectCopier(source_xnat, source_project, dest_xnat, dest_project)
            copier.start()


if __name__ == '__main__':
    main()
