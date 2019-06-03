""" Fixtures files for type version manager
"""
from core_composer_app.components.bucket.models import Bucket
from tests.components.type_version_manager.fixtures.fixtures import TypeVersionManagerFixtures


class BucketFixtures(TypeVersionManagerFixtures):
    """ Bucket fixtures
    """
    bucket_empty = None
    bucket_1 = None
    bucket_2 = None
    bucket_collection = None

    def insert_data(self):
        """ Insert a set of Buckets.

        Returns:

        """
        super(BucketFixtures, self).insert_data()

        self.bucket_empty = Bucket(label="empty",
                                   color='#000000',
                                   types=[]).save()
        self.bucket_1 = Bucket(label='bucket1',
                               color='#000001',
                               types=[self.type_vm_1]).save()
        self.bucket_2 = Bucket(label='bucket2',
                               color='#000002',
                               types=[self.type_vm_1, self.type_vm_2]).save()

        self.bucket_collection = [self.bucket_empty,
                                  self.bucket_1,
                                  self.bucket_2]
