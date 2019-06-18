import uuid


class Guid:

    def Generate(self):
        return str(uuid.uuid4())

    def GenerateAlphanumeric(self):
        return str(uuid.uuid4()).replace('-', '')