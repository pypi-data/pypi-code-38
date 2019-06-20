from datetime import datetime
from typing import Dict, List

from pyvko.attachment import Attachment


class Post:
    def __init__(self, text: str = None, attachments: List[Attachment] = None, date: datetime = None) -> None:
        self.date = date
        self.attachments = attachments
        self.id = None
        self.text = text
        self.timer_id = None

    def __str__(self) -> str:
        return f"Post: {self.id} | {self.text}"

    @staticmethod
    def from_post_object(post_object: Dict) -> 'Post':
        if "attachments" in post_object:
            attachments = [Attachment.from_object(o) for o in post_object["attachments"]]
        else:
            attachments = None

        post = Post(
            text=post_object["text"],
            date=datetime.fromtimestamp(post_object["date"]),
            attachments=attachments
        )

        post.id = post_object["id"]

        if "postponed_id" in post_object:
            post.timer_id = post_object["postponed_id"]

        return post

    def to_request(self) -> dict:
        request = {}

        if self.id is not None:
            request["post_id"] = self.id

        if self.text is not None:
            request["message"] = self.text

        if self.attachments is not None:
            request["attachments"] = ",".join([a.to_attach() for a in self.attachments])

        if self.date is not None:
            request["publish_date"] = self.date.timestamp()

        return request
