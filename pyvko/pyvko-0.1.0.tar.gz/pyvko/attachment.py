from enum import Enum, auto


class Attachment:
    class Type(Enum):
        PHOTO = auto()

    def __init__(self, self_id: int, owner_id: int, attach_type) -> None:
        super().__init__()

        self.type: Attachment.Type = attach_type
        self.id = self_id
        self.owner_id = owner_id

    def to_attach(self) -> str:
        return f"photo{self.owner_id}_{self.id}"

    @staticmethod
    def parse_photo(api_object: dict) -> 'Attachment':
        owner_id = api_object["owner_id"]
        self_id = api_object["id"]

        return Attachment(self_id, owner_id, Attachment.Type.PHOTO)

    @staticmethod
    def from_object(api_object: dict):
        return Attachment.parse_photo(api_object["photo"])
