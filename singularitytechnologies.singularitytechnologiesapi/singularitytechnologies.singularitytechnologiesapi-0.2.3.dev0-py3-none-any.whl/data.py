import hashlib
import io
import os
import random
import zipfile

import asyncio


SHARD_MAX_SIZE = 10 * 1024 * 1024
SHARD_BATCH_SIZE = 100


class Sharder(object):
    def __init__(self, location):
        if not location.endswith('/'):
            location = '%s/' % location

        self.location = location

    async def __generate_file_imprint(self, root, filename):
        file_path = os.path.join(root, filename)
        with open(file_path, 'rb') as f:
            contents = f.read()
            hash_id = hashlib.sha256(contents).hexdigest()
            local_path = file_path.replace(self.location, '')
            return {'path': local_path, 'hash_id': hash_id, 'size': len(contents)}

    def __find_files(self):
        files_to_shard = []
        event_loop = asyncio.get_event_loop()

        for root, _, filenames in os.walk(self.location):
            tasks = []
            for filename in filenames:
                tasks.append(self.__generate_file_imprint(root, filename))

            future = asyncio.gather(*tasks)
            files_to_shard += event_loop.run_until_complete(future)

        event_loop.close()

        return files_to_shard

    def __generate_shard(self, ram_file, shard_files):
        ram_file.seek(0)
        contents = ram_file.read()
        shard_id = hashlib.sha256(contents).hexdigest()

        for sharded_fileinfo in shard_files:
            sharded_fileinfo.pop('path')
            sharded_fileinfo['shard_id'] = shard_id

        return shard_id, contents

    def get_new_shards(self):
        # This function acts as a generator, creating & yielding shards to be
        # sent to the api
        os.chdir(self.location)

        shard_size = 0
        shard_files = []
        ram_file = io.BytesIO()
        ziped = zipfile.ZipFile(ram_file, 'w')

        local_files = self.__find_files()
        left = len(local_files)
        batches = []
        start = 0
        end = SHARD_BATCH_SIZE
        while True:
            batches.append(local_files[start:end])
            start += SHARD_BATCH_SIZE
            end += SHARD_BATCH_SIZE

            if start > left:
                break

            if end > left:
                end = left

        left = len(batches)
        while left:
            index = random.randint(0, left-1)
            batch = batches.pop(index)

            for fileinfo in batch:
                size = fileinfo.get('size', 0)
                if shard_size + size > SHARD_MAX_SIZE:
                    ziped.close()

                    yield self.__generate_shard(ram_file, shard_files)

                    shard_size = 0
                    shard_files = []
                    ram_file = io.BytesIO()
                    ziped = zipfile.ZipFile(ram_file, 'w')

                ziped.write(fileinfo.get('path'))
                shard_size += size
                shard_files.append(fileinfo)

            left -= 1
            if left <= 0:
                ziped.close()
                yield self.__generate_shard(ram_file, shard_files)
