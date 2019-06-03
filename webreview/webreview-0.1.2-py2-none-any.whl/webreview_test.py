import os
import unittest
from . import webreview


TEST_BUILD_DIR = os.path.join(
    os.path.dirname(__file__), 'testdata', 'build')


class WebReviewTestCase(unittest.TestCase):

    @unittest.skipIf("TRAVIS" in os.environ and os.environ["TRAVIS"] == "true",
                     "Skipping this test on Travis CI.")
    def test_exception(self):
        def raise_error():
            raise webreview.GoogleStorageRpcError(403, 'Forbidden.')
        self.assertRaises(webreview.GoogleStorageRpcError, raise_error)

    def test_client(self):
        self.assertRaises(ValueError, webreview.WebReview, 'foo', 'bar', 'baz')

        client = webreview.WebReview(
            project='jeremydw/test',
            name='test-staging-site',
            host='grow-prod.appspot.com',
            secure=True,)
        client.login()

        # Upload directory.
        paths_written, errors = client.upload_dir(TEST_BUILD_DIR)
        for basename in os.listdir(TEST_BUILD_DIR):
            self.assertIn('/{}'.format(basename), paths_written)
        self.assertEqual({}, errors)

        # Write.
        paths_to_rendered_doc = {
            '/foo.html': webreview.RenderedDocStub('/foo.html', 'hello foo'),
            '/bar.html': webreview.RenderedDocStub('/bar.html', 'hello bar'),
        }
        paths_written, errors = client.write(paths_to_rendered_doc)
        for path in paths_to_rendered_doc:
            self.assertIn(path, paths_written)
        self.assertEqual({}, errors)

        # Read.
        paths_read, errors = client.read(paths_to_rendered_doc.keys())
        for path, content in paths_read.iteritems():
            self.assertEqual(paths_to_rendered_doc[path].content, content)
        self.assertEqual({}, errors)

        # Delete.
        deleted_path = paths_to_rendered_doc.keys()[1]
        paths_deleted, errors = client.delete([deleted_path])
        self.assertIn(deleted_path, paths_deleted)
        self.assertEqual({}, errors)

        # Error on reading deleted file.
        paths_read, errors = client.read([deleted_path])
        self.assertEqual({}, paths_read)
        self.assertTrue(isinstance(
            errors[deleted_path], webreview.GoogleStorageRpcError))


if __name__ == '__main__':
    unittest.main()
