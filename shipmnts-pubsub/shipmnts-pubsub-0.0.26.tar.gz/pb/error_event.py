import json
import logging
import os
from google.cloud import pubsub_v1

publisher = pubsub_v1.PublisherClient()

def publish_to_error(data, project_id, topic_name):
    """Publishes multiple messages to a Pub/Sub topic with an error handler."""
    topic_path = publisher.topic_path(project_id, topic_name)

    logging.info("%s FOR ERROR_HANDLER_TOPIC TOPIC", topic_path)

    def callback(message_future):
        # When timeout is unspecified, the exception method waits indefinitely.
        if message_future.exception(timeout=10):
            logging.info(
                "Publishing message on %s threw an Exception %s",
                topic_name,
                message_future.exception(),
            )
        else:
            logging.info("publish_to_error id %s",
                         message_future.result())

    data = json.dumps(data).encode("utf-8")
    message_future = publisher.publish(topic_path, data=data)
    message_future.add_done_callback(callback)
    message_future.result()
