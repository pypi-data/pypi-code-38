from spell.api import base_client


USER_RESOURCE_URL = "feedback"


class FeedbackClient(base_client.BaseClient):

    def post_feedback(self, content):
        """Post feedback to the team.

        Keyword arguments:
        content -- the content of the feedback to post

        Returns:
        None
        """
        payload = {
            "content": content,
        }
        r = self.request("post", USER_RESOURCE_URL, payload=payload)
        self.check_and_raise(r)
