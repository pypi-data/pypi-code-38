import gzip
import io
import rapidjson as rj

for i in range(2):
    with open('/tmp/test.gz', 'rb') as f:
        content = f.read()
        with io.BytesIO(content) as file_object:
            with gzip.GzipFile(fileobj=file_object, filename='test.json') as archive:
                rj.load(archive)
