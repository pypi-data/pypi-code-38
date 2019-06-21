class GcsDataSource():
    def get_file_keys(self) -> list:
        pass

    def new_file_by_force_resource(self, resources: List):
        pass

    def copy_from_datasource(self, filename: str):
        pass

    def upload_to_datasource(self, data_json: str, job_id: str):
        pass

