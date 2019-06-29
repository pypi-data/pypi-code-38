import os
import shutil
import tempfile

import requests

from ioflow.model_saver.model_saver_base import ModelSaverBase


class HttpBasedModelSaver(ModelSaverBase):
    def save_model(self, model_path, corpus_path=None):
        files = []

        zipped_model = os.path.join(tempfile.mkdtemp(), 'model')
        model_zip_path = shutil.make_archive(zipped_model, 'zip', model_path)
        files.append(
            ('multipartFiles', ('model.zip', open(model_zip_path, 'rb'), 'application/zip', {'Expires': '0'}))
        )

        if corpus_path:
            zipped_corpus = os.path.join(tempfile.mkdtemp(), 'corpus')
            corpus_zip_path = shutil.make_archive(zipped_corpus, 'zip', model_path)

            files.append(
                ('multipartFiles', ('corpus.zip', open(corpus_zip_path, 'rb'), 'application/zip', {'Expires': '0'}))
            )

        r = requests.post(self.config['model_saver_url'],
                          data={'id': self.config['task_id']},
                          files=files)

        print(r.content)

        print(r.status_code)

        return model_zip_path


if __name__ == "__main__":
    config = {
        # 'model_saver_scheme': 'http',
        'model_saver_url': 'http://10.43.10.17:25005/hdfs/upload',
        # 'model_saver_url': 'http://127.0.0.1:8080/hdfs/upload',
        'task_id': '5ce3dfe15148635a5c04a688'
    }

    processor = HttpBasedModelSaver(config)
    # zipped_file = processor.save_model(os.path.dirname(__file__))

    # big file
    zipped_file = processor.save_model(os.path.dirname(__file__))

    print(zipped_file)
