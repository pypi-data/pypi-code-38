import filecmp
import glob
import os
import shutil
import tempfile
import unittest
import zipfile

from . import bundler

class TestBundler(unittest.TestCase):
    FIXTURES_DIR = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'fixtures'
    )
    TEST_MODEL_DIR = os.path.join(FIXTURES_DIR, 'test-model')
    TEST_TFLITE_FILE = os.path.join(FIXTURES_DIR, 'test.tflite')
    TEST_TIOBUNDLE = os.path.join(FIXTURES_DIR, 'test.tiobundle')
    NESTED_ASSETS_TIOBUNDLE = os.path.join(FIXTURES_DIR, 'nested-assets-dir.tiobundle')
    SAVED_MODEL_TIOBUNDLE = os.path.join(FIXTURES_DIR, 'savedmodel.tiobundle')

    def setUp(self):
        self.output_directories = []

    def tearDown(self):
        for output_directory in self.output_directories:
            shutil.rmtree(output_directory)

    def create_temp_dir(self):
        temp_dir = tempfile.mkdtemp()
        self.output_directories.append(temp_dir)
        return temp_dir

    def test_tflite_build_from_saved_model(self):
        outdir = self.create_temp_dir()
        tflite_file = os.path.join(outdir, 'model.tflite')
        bundler.tflite_build_from_saved_model(self.TEST_MODEL_DIR, tflite_file)
        self.assertTrue(filecmp.cmp(tflite_file, self.TEST_TFLITE_FILE))

    def test_tflite_build_from_saved_model_when_outfile_already_exists(self):
        outdir = self.create_temp_dir()
        tflite_file = os.path.join(outdir, 'model.tflite')
        with open(tflite_file, 'w') as outfile:
            outfile.write('dummy')
        with self.assertRaises(bundler.TFLiteFileExistsError):
            bundler.tflite_build_from_saved_model(self.TEST_MODEL_DIR, tflite_file)

    def test_tflite_build_from_saved_model_with_no_saved_model_dir(self):
        outdir = self.create_temp_dir()
        nonexistent_saved_model_dir = os.path.join(outdir, 'saved_model_dir')
        tflite_file = os.path.join(outdir, 'model.tflite')
        with self.assertRaises(bundler.SavedModelDirMisspecificationError):
            bundler.tflite_build_from_saved_model(nonexistent_saved_model_dir, tflite_file)

    def test_tflite_build_from_saved_model_with_file_instead_of_saved_model_dir(self):
        outdir = self.create_temp_dir()
        dummy_file = os.path.join(outdir, 'saved_model_dir')
        with open(dummy_file, 'w') as ofp:
            ofp.write('dummy')
        tflite_file = os.path.join(outdir, 'model.tflite')
        with self.assertRaises(bundler.SavedModelDirMisspecificationError):
            bundler.tflite_build_from_saved_model(dummy_file, tflite_file)

    def test_tiobundle_build(self):
        outdir = self.create_temp_dir()
        outfile = os.path.join(outdir, 'test.tiobundle.zip')
        tiobundle_name = 'actual.tiobundle'
        bundler.tiobundle_build(
            os.path.join(self.TEST_TIOBUNDLE, 'model.tflite'),
            os.path.join(self.TEST_TIOBUNDLE, 'model.json'),
            os.path.join(self.TEST_TIOBUNDLE, 'assets'),
            tiobundle_name,
            outfile
        )

        extraction_dir = self.create_temp_dir()
        with zipfile.ZipFile(outfile, 'r') as tiobundle_zip:
            tiobundle_zip.extractall(path=extraction_dir)

        extracted_paths_glob = os.path.join(extraction_dir, tiobundle_name, '**/*')
        extracted_paths = glob.glob(extracted_paths_glob, recursive=True)

        expected_files = {'model.tflite', 'model.json', 'assets', 'assets/labels.txt'}
        self.assertEqual(len(extracted_paths), len(expected_files))

        expected_paths = {
            os.path.join(extraction_dir, tiobundle_name, expected_file)
            for expected_file in expected_files
        }
        self.assertSetEqual(set(extracted_paths), expected_paths)

    def test_savedmodel_tiobundle_build(self):
        outdir = self.create_temp_dir()
        outfile = os.path.join(outdir, 'savedmodel.tiobundle.zip')
        tiobundle_name = 'actual.tiobundle'
        bundler.tiobundle_build(
            os.path.join(self.SAVED_MODEL_TIOBUNDLE, 'train'),
            os.path.join(self.SAVED_MODEL_TIOBUNDLE, 'model.json'),
            os.path.join(self.SAVED_MODEL_TIOBUNDLE, 'assets'),
            tiobundle_name,
            outfile
        )

        extraction_dir = self.create_temp_dir()
        with zipfile.ZipFile(outfile, 'r') as tiobundle_zip:
            tiobundle_zip.extractall(path=extraction_dir)

        extracted_paths_glob = os.path.join(extraction_dir, tiobundle_name, '**/*')
        extracted_paths = glob.glob(extracted_paths_glob, recursive=True)

        expected_files = {
            'train',
            'train/saved_model.pb',
            'train/variables',
            'train/variables/variables.index',
            'train/variables/variables.data-00000-of-00001',
            'model.json',
            'assets',
            'assets/labels.txt'
        }
        self.assertEqual(len(extracted_paths), len(expected_files))

        expected_paths = {
            os.path.join(extraction_dir, tiobundle_name, expected_file)
            for expected_file in expected_files
        }
        self.assertSetEqual(set(extracted_paths), expected_paths)

    def test_savedmodel_tiobundle_build_with_invalid_model_json(self):
        outdir = self.create_temp_dir()
        outfile = os.path.join(outdir, 'savedmodel.tiobundle.zip')
        tiobundle_name = 'actual.tiobundle'
        with self.assertRaises(bundler.InvalidBundleSpecification):
            bundler.tiobundle_build(
                os.path.join(self.SAVED_MODEL_TIOBUNDLE, 'train'),
                os.path.join(self.SAVED_MODEL_TIOBUNDLE, 'invalid_model.json'),
                os.path.join(self.SAVED_MODEL_TIOBUNDLE, 'assets'),
                tiobundle_name,
                outfile
            )

    def test_tiobundle_build_with_nested_assets(self):
        outdir = self.create_temp_dir()
        outfile = os.path.join(outdir, 'test.tiobundle.zip')
        tiobundle_name = 'actual.tiobundle'
        bundler.tiobundle_build(
            os.path.join(self.NESTED_ASSETS_TIOBUNDLE, 'model.tflite'),
            os.path.join(self.NESTED_ASSETS_TIOBUNDLE, 'model.json'),
            os.path.join(self.NESTED_ASSETS_TIOBUNDLE, 'assets'),
            tiobundle_name,
            outfile
        )

        extraction_dir = self.create_temp_dir()
        with zipfile.ZipFile(outfile, 'r') as tiobundle_zip:
            tiobundle_zip.extractall(path=extraction_dir)

        extracted_paths_glob = os.path.join(extraction_dir, tiobundle_name, '**/*')
        extracted_paths = glob.glob(extracted_paths_glob, recursive=True)

        expected_files = {
            'model.tflite',
            'model.json',
            'assets',
            'assets/labels.txt',
            'assets/labels2.txt',
            'assets/misc',
            'assets/misc/misc.txt'
        }
        self.assertEqual(len(extracted_paths), len(expected_files))

        expected_paths = {
            os.path.join(extraction_dir, tiobundle_name, expected_file)
            for expected_file in expected_files
        }
        self.assertSetEqual(set(extracted_paths), expected_paths)

    def test_tiobundle_build_when_outfile_already_exists(self):
        outdir = self.create_temp_dir()
        outfile = os.path.join(outdir, 'test.tiobundle.zip')
        with open(outfile, 'w') as ofp:
            ofp.write('dummy')
        tiobundle_name = 'actual.tiobundle'
        with self.assertRaises(bundler.ZippedTIOBundleExistsError):
            bundler.tiobundle_build(
                os.path.join(self.TEST_TIOBUNDLE, 'model.tflite'),
                os.path.join(self.TEST_TIOBUNDLE, 'model.json'),
                os.path.join(self.TEST_TIOBUNDLE, 'assets'),
                tiobundle_name,
                outfile
            )

    def test_tiobundle_build_when_tflite_path_does_not_exist(self):
        outdir = self.create_temp_dir()
        outfile = os.path.join(outdir, 'test.tiobundle.zip')
        tiobundle_name = 'actual.tiobundle'
        with self.assertRaises(bundler.ZippedTIOBundleMisspecificationError):
            bundler.tiobundle_build(
                os.path.join(outdir, 'model.tflite'),
                os.path.join(self.TEST_TIOBUNDLE, 'model.json'),
                os.path.join(self.TEST_TIOBUNDLE, 'assets'),
                tiobundle_name,
                outfile
            )

    def test_tiobundle_build_when_model_json_path_does_not_exist(self):
        outdir = self.create_temp_dir()
        outfile = os.path.join(outdir, 'test.tiobundle.zip')
        tiobundle_name = 'actual.tiobundle'
        with self.assertRaises(bundler.ZippedTIOBundleMisspecificationError):
            bundler.tiobundle_build(
                os.path.join(self.TEST_TIOBUNDLE, 'model.tflite'),
                os.path.join(outdir, 'model.json'),
                os.path.join(self.TEST_TIOBUNDLE, 'assets'),
                tiobundle_name,
                outfile
            )

    def test_tiobundle_build_when_model_json_path_is_not_file(self):
        outdir = self.create_temp_dir()
        outfile = os.path.join(outdir, 'test.tiobundle.zip')
        tiobundle_name = 'actual.tiobundle'
        model_json_path = os.path.join(outdir, 'model.json')
        os.mkdir(model_json_path)
        with self.assertRaises(bundler.ZippedTIOBundleMisspecificationError):
            bundler.tiobundle_build(
                os.path.join(self.TEST_TIOBUNDLE, 'model.tflite'),
                model_json_path,
                os.path.join(self.TEST_TIOBUNDLE, 'assets'),
                tiobundle_name,
                outfile
            )
