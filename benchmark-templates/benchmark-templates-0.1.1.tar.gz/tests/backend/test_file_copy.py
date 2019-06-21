"""Test various methods that copy input and output files for workflow runs."""

import os
import shutil

from unittest import TestCase

from benchtmpl.backend.util import FileCopy
from benchtmpl.io.files.base import FileHandle
from benchtmpl.workflow.parameter.value import TemplateArgument
from benchtmpl.workflow.template.base import TemplateHandle
from benchtmpl.workflow.template.repo import TemplateRepository

import benchtmpl.error as err
import benchtmpl.backend.util as backend


DATA_FILE = './tests/files/workflows/helloworld/data/names.txt'
TMP_DIR = './tests/files/.tmp'
INPUT_DIR = './tests/files/workflows/helloworld'
INPUT_FILE = './tests/files/schema.json'
SPEC_FILE = 'alt-template.yaml'
SPEC_FILE_ERR = 'alt-error.yaml'
WORKFLOW_DIR = './tests/files/template'


class TestFileCopy(TestCase):
    """Test copying files on local disk for workflow run preparation."""
    def setUp(self):
        """Create an empty target directory for each test and intitialize the
        file loader function.
        """
        self.tearDown()
        os.makedirs(TMP_DIR)
        self.loader = FileCopy(TMP_DIR)

    def tearDown(self):
        """Remove the temporary target directory."""
        if os.path.isdir(TMP_DIR):
            shutil.rmtree(TMP_DIR)

    def test_input_dir_copy(self):
        """Test copying local directories into a workflow run directory."""
        # Copy file to target directory
        self.loader(source=INPUT_DIR, target='workflow')
        dirname = os.path.join(TMP_DIR, 'workflow')
        self.assertTrue(os.path.isdir(dirname))
        self.assertTrue(os.path.isdir(os.path.join(dirname, 'code')))
        datadir = os.path.join(dirname, 'data')
        self.assertTrue(os.path.isdir(datadir))
        self.assertTrue(os.path.isfile(os.path.join(datadir, 'names.txt')))
        # Copy to target directory under parent that does not exist
        dst = os.path.join('run', 'files', 'wf')
        self.loader(source=INPUT_DIR, target=dst)
        dirname = os.path.join(TMP_DIR, dst)
        self.assertTrue(os.path.isdir(dirname))
        self.assertTrue(os.path.isdir(os.path.join(dirname, 'code')))
        datadir = os.path.join(dirname, 'data')
        self.assertTrue(os.path.isdir(datadir))
        self.assertTrue(os.path.isfile(os.path.join(datadir, 'names.txt')))

    def test_input_file_copy(self):
        """Test copying local input files into a workflow run directory."""
        # Copy file to target directory
        self.loader(source=INPUT_FILE, target='input.data')
        self.assertTrue(os.path.isfile(os.path.join(TMP_DIR, 'input.data')))
        # Copy file to non-existing target directory
        target = os.path.join('data', 'input.data')
        self.loader(source=INPUT_FILE, target=target)
        self.assertTrue(os.path.isfile(os.path.join(TMP_DIR, target)))

    def test_prepare_inputs_for_local_run(self):
        """Test copying input files for a local workflow run."""
        # Load template
        store = TemplateRepository(base_dir=TMP_DIR)
        template = store.add_template(
            src_dir=WORKFLOW_DIR,
            template_spec_file=os.path.join(WORKFLOW_DIR, SPEC_FILE)
        )
        # Create run directory
        run_dir = os.path.join(TMP_DIR, 'run')
        os.makedirs(run_dir)
        # Copy input files to run directory
        backend.upload_files(
            template=template,
            files=template.workflow_spec.get('inputs', {}).get('files', []),
            arguments={
                'names': TemplateArgument(
                    template.get_parameter('names'),
                    value=FileHandle(filepath=DATA_FILE)
                )
            },
            loader=FileCopy(run_dir)
        )
        # We should have the following files in the run directory:
        # code/helloworld.py
        # data/persons.txt
        # data/friends.txt
        self.assertTrue(os.path.isfile(os.path.join(run_dir, 'code', 'helloworld.py')))
        self.assertTrue(os.path.isfile(os.path.join(run_dir, 'data', 'persons.txt')))
        self.assertTrue(os.path.isfile(os.path.join(run_dir, 'data', 'friends.txt')))
        # data/persons.txt should contain Alice and Bob
        names = set()
        with open(os.path.join(run_dir, 'data', 'persons.txt'), 'r') as f:
            for line in f:
                names.add(line.strip())
        self.assertEqual(len(names), 2)
        self.assertTrue('Alice' in names)
        self.assertTrue('Bob' in names)
        # data/friends contains Jane Doe and Joe Bloggs
        friends = set()
        with open(os.path.join(run_dir, 'data', 'friends.txt'), 'r') as f:
            for line in f:
                friends.add(line.strip())
        self.assertEqual(len(friends), 2)
        self.assertTrue('Jane Doe' in friends)
        self.assertTrue('Joe Bloggs' in friends)
        # Error cases
        with self.assertRaises(err.MissingArgumentError):
            backend.upload_files(
                template=template,
                files=template.workflow_spec.get('inputs', {}).get('files', []),
                arguments={},
                loader=FileCopy(run_dir)
            )
        # Error when copying non-existing file
        template = store.add_template(
            src_dir=WORKFLOW_DIR,
            template_spec_file=os.path.join(WORKFLOW_DIR, SPEC_FILE)
        )
        shutil.rmtree(run_dir)
        os.makedirs(run_dir)
        with self.assertRaises(IOError):
            backend.upload_files(
                template=template,
                files=template.workflow_spec.get('inputs', {}).get('files', []),
                arguments={
                    'names': TemplateArgument(
                        template.get_parameter('names'),
                        value=FileHandle(filepath=os.path.join(TMP_DIR, 'no.file'))
                    )
                },
                loader=FileCopy(run_dir)
            )
        self.assertFalse(os.path.isdir(os.path.join(run_dir, 'data')))
        # If the constant value for the names parameter is removed the names
        # file is copied to the run directory and not to the data folder
        para = template.get_parameter('names')
        para.as_constant = None
        shutil.rmtree(run_dir)
        os.makedirs(run_dir)
        backend.upload_files(
            template=template,
            files=template.workflow_spec.get('inputs', {}).get('files', []),
            arguments={
                'names': TemplateArgument(
                    parameter=para,
                    value=FileHandle(filepath=DATA_FILE)
                )
            },
            loader=FileCopy(run_dir)
        )
        # We should have the following files in the run directory:
        # code/helloworld.py
        # names.txt
        # data/friends.txt
        self.assertTrue(os.path.isfile(os.path.join(run_dir, 'code', 'helloworld.py')))
        self.assertTrue(os.path.isfile(os.path.join(run_dir, 'names.txt')))
        self.assertFalse(os.path.isfile(os.path.join(run_dir, 'data', 'persons.txt')))
        self.assertTrue(os.path.isfile(os.path.join(run_dir, 'data', 'friends.txt')))
        # Template with input file parameter that is not of type file
        template = store.add_template(
            src_dir=WORKFLOW_DIR,
            template_spec_file=os.path.join(WORKFLOW_DIR, SPEC_FILE_ERR)
        )
        shutil.rmtree(run_dir)
        os.makedirs(run_dir)
        # Copy input files to run directory
        with self.assertRaises(err.InvalidTemplateError):
            backend.upload_files(
                template=template,
                files=template.workflow_spec.get('inputs', {}).get('files', []),
                arguments={
                    'sleeptime': TemplateArgument(
                        template.get_parameter('names'),
                        value=FileHandle(filepath=DATA_FILE)
                    )
                },
                loader=FileCopy(run_dir)
            )


if __name__ == '__main__':
    import unittest
    unittest.main()
