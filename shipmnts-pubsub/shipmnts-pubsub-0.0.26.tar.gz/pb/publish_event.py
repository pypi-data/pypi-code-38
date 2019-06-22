import logging
import json
from google.cloud import pubsub_v1

publisher = pubsub_v1.PublisherClient()
def publish_event(data, project_id, topic_name):
    """Publishes multiple messages to a Pub/Sub topic with an error handler."""
    topic_path = publisher.topic_path(project_id, topic_name)
    logging.info("{} Topic Path".format(topic_path))

    def callback(message_future):
        # When timeout is unspecified, the exception method waits indefinitely.
        if message_future.exception(timeout=30):
            logging.info(
                "Publishing message on {} threw an Exception {}.".format(
                    topic_name, message_future.exception()
                )
            )
        else:
            logging.info(message_future.result())

    logging.info("Published message IDs:")
    data = json.dumps(data).encode("utf-8")
    message_future = publisher.publish(topic_path, data=data)
    message_future.add_done_callback(callback)
    message_future.result()
 