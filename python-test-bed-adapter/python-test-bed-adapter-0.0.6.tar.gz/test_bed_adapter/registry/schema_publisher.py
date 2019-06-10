import asyncio
import logging
import requests
import json
import os
from .schema_access import SchemaAccess
from ..utils.helpers import Helpers


class SchemaPublisher(SchemaAccess):
    def __init__(self, test_bed_options):
        super().__init__(test_bed_options)
        self.default_schema = "default_schema.json"
        self.schema_folder = test_bed_options.schema_folder
        self.auto_register_schemas = test_bed_options.auto_register_schemas
        file_path = os.path.dirname(os.path.abspath(__file__))
        self.default_schema_path = os.path.join(file_path, self.default_schema)

    def start_process(self):
        if self.schema_folder and self.auto_register_schemas:
            self.is_schema_registry_available()

            if self.schema_available:
                files = Helpers.find_files_in_dir(self.schema_folder)
                missing_key_files = Helpers.missing_key_files(files)
                files_upload = files + missing_key_files
                for schema_file in files_upload:
                    use_default_schema = schema_file in missing_key_files
                    self.post_schema(schema_file, use_default_schema)

    def post_schema(self, schema_filename: str, use_default_schema: bool):
        schema_topic = os.path.basename(schema_filename).replace(".avsc", "")
        upload_url = self.schema_url + "/subjects/"+schema_topic+"/versions"
        default_schema_file = open(self.default_schema_path, encoding="utf-8")
        default_schema = json.loads(default_schema_file.read())
        default_schema_file.close()
        if use_default_schema:
            schema = default_schema
        else:
            schema_file = open(schema_filename, encoding="utf-8")
            schema = json.loads(schema_file.read())
            schema_file.close()

        data = {"schema": json.dumps(schema)}
        headers = {"Content-type": "application/vnd.schemaregistry.v1+json"}
        try:
            response = requests.post(url=upload_url, json=data, headers=headers)
            message = "Uploaded schema " + schema_topic + " to " + upload_url + " with default key schema " \
                if use_default_schema else "Uploaded schema " + schema_topic + " to " + upload_url
            message = message + ". Response from server: " + response.text
            if response.status_code != 200:
                raise Exception(response.text)
            logging.info(message)
        except Exception as error:
            logging.error("Error uploading schema " + schema_topic + " to " + upload_url)
            logging.error(error)


