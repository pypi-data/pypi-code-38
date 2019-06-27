from airflow.utils.decorators import apply_defaults
from airflow.contrib.sensors.pubsub_sensor import PubSubPullSensor
from airflow.contrib.hooks.gcp_pubsub_hook import PubSubHook
from airflow.contrib.operators.pubsub_operator import (
    PubSubSubscriptionCreateOperator,
    PubSubTopicDeleteOperator,
    PubSubSubscriptionDeleteOperator
)
import base64


class SharedTopicPubSubPullSensor(PubSubPullSensor):
    """
        A pubsub pull sensor that can be set to listen for a specific trigger message
        from a central pubsub topic that's shared among many publishers and subscribers.
        Different instances of the sensor can be set to listen for different messages.
        :param project: the GCP project ID where the topic and subscriptions live (templated)
        :type project: str
        :param subscription: the Pub/Sub subscription name. Do not include the
            full subscription path.
        :type subscription: str
        :param trigger_msg: message the sensor is waiting for from the topic
        :type trigger_msg: str
        :param max_messages: The maximum number of messages to retrieve per
            PubSub pull request
        :type max_messages: int
        :param return_immediately: If True, instruct the PubSub API to return
            immediately if no messages are available for delivery.
        :type return_immediately: bool
        :param ack_messages: If True, each message will be acknowledged
            immediately rather than by any downstream tasks
        :type ack_messages: bool
        :param gcp_conn_id: The connection ID to use connecting to
            Google Cloud Platform.
        :type gcp_conn_id: str
        :param delegate_to: The account to impersonate, if any.
            For this to work, the service account making the request
            must have domain-wide delegation enabled.
        :type delegate_to: str
    """
    @apply_defaults
    def __init__(
            self,
            project,
            subscription,
            trigger_msg,
            max_messages=100000,
            return_immediately=True,
            ack_messages=True,
            gcp_conn_id='google_cloud_default',
            delegate_to=None,
            poke_interval=60,
            timeout=180,
            *args,
            **kwargs):

        super(
            SharedTopicPubSubPullSensor,
            self).__init__(
            poke_interval=poke_interval,
            timeout=timeout,
            *args,
            **kwargs)

        self.gcp_conn_id = gcp_conn_id
        self.delegate_to = delegate_to
        self.project = project
        self.subscription = subscription
        self.max_messages = max_messages
        self.return_immediately = return_immediately
        self.ack_messages = ack_messages
        self._messages = None
        self.trigger_msg = trigger_msg

    def poke(self, context):
        self.log.info("poking...")
        hook = PubSubHook(gcp_conn_id=self.gcp_conn_id,
                          delegate_to=self.delegate_to)
        self.log.info("pulling messages...")
        self._messages = hook.pull(
            self.project, self.subscription, self.max_messages,
            self.return_immediately)
        if not self._messages:
            self.log.info("no messages found")
        elif self._messages and self.ack_messages:
            self.log.info("found " + str(len(self._messages)) + " message(s)")
            # This section is just to log info about the message.  It's been left
            # in to help with debugging production problems,
            for mes in self._messages:
                self.log.info(
                    "data: " +
                    base64.b64decode(
                        mes['message']['data']))
                for k, v in mes.iteritems():
                    self.log.info("key: " + str(k))
                    self.log.info("value: " + str(v))
            # Check each pulled message and see if it contains the trigger
            # message the sensor is waiting for. If it does then add the
            # message ackId to an array.
            ack_ids = [m['ackId'] for m in self._messages if m.get('ackId')
                       and m.get('message')
                       and base64.b64decode(m['message']['data']) == self.trigger_msg]
            if len(ack_ids) > 0:
                self.log.info("found trigger message.  Acknowledging message")
                hook.acknowledge(self.project, self.subscription, ack_ids)
                return [msg for msg in self._messages if msg.get(
                    'ackId') and msg['ackId'] in ack_ids]


class SharedTopicSubscriptionTaskSet:

    """
        A convenience class for more easily creating the two operators and one sensor
        needed to subscribe to a pubsub topic, listen for a specific message and
        then delete the subscription once the message has been received.
        :param dag: the dag the airflow tasks will be added onto
        :type dag: dag
        :param gcp_conn_id: the connection to use to talk to the pubsub topic
        :type gcp_conn_id: str
        :param project: the GCP project ID where the topic and subscriptions live (templated)
        :type project: str
        :param topic: the pubsub topic that will be used to pass the trigger message
        :type topic : string
        :param subscription: the Pub/Sub subscription name. Do not include the
            full subscription path.
        :type subscription: str
        :param trigger_msg: the message being listened for from the pubsub topic
        :type trigger_msg: str
    """

    def __init__(
            self,
            dag,
            gcp_conn_id,
            project,
            topic,
            subscription,
            trigger_msg):
        self.dag = dag
        self.topic_project = project
        self.trigger_msg = trigger_msg
        self.gcp_conn_id = gcp_conn_id
        self.topic = topic
        self.subscription = subscription

    @property
    def create_subscription_task(self):
        return PubSubSubscriptionCreateOperator(
            task_id='create_subscription', topic_project=self.topic_project,
            topic=self.topic, subscription=self.subscription,
            dag=self.dag)

    @property
    def sensor_task(self):
        return SharedTopicPubSubPullSensor(
            task_id='trigger_msg_sensor',
            project=self.topic_project,
            subscription=self.subscription,
            trigger_msg=self.trigger_msg,
            gcp_conn_id=self.gcp_conn_id,
            topic=self.topic,
            max_messages=2,
            ack_messages=True,
            dag=self.dag)

    @property
    def delete_subscription_task(self):
        return PubSubSubscriptionDeleteOperator(
            task_id='delete_subscription',
            project=self.topic_project,
            stopic=self.topic, subscription=self.subscription,
            gcp_conn_id=self.gcp_conn_id,
            dag=self.dag)
