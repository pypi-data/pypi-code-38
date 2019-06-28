from airflow.utils.decorators import apply_defaults
from airflow.contrib.sensors.pubsub_sensor import PubSubPullSensor
from airflow.contrib.hooks.gcp_pubsub_hook import PubSubHook
from airflow.contrib.operators.pubsub_operator import (
    PubSubTopicCreateOperator, PubSubSubscriptionCreateOperator,
    PubSubPublishOperator, PubSubTopicDeleteOperator,
    PubSubSubscriptionDeleteOperator
)


class CustomPubSubPullSensor(PubSubPullSensor):

    @apply_defaults
    def __init__(self, project, subscription, max_messages=5, return_immediately=False,
                 ack_messages=False, gcp_conn_id='google_cloud_default',
                 delegate_to=None, *args, **kwargs):

        super(PubSubPullSensor, self).__init__(*args, **kwargs)

        self.gcp_conn_id = gcp_conn_id
        self.delegate_to = delegate_to
        self.project = project
        self.subscription = subscription
        self.max_messages = max_messages
        self.return_immediately = return_immediately
        self.ack_messages = ack_messages

        self._messages = None

    def execute(self, context):
        return super(CustomPubSubPullSensor, self).execute(context)

    def poke(self, context):
        hook = PubSubHook(gcp_conn_id=self.gcp_conn_id,
                          delegate_to=self.delegate_to)
        self._messages = hook.pull(
            self.project, self.subscription, self.max_messages,
            self.return_immediately)
        if self._messages and self.ack_messages:
            if self.ack_messages:
                ack_ids = [m['ackId'] for m in self._messages if m.get('ackId')
                           and m.get('message') and m['message'].get('attributes')
                           and m['message']['attributes'].get('event_type')
                           and m['message']['attributes']['event_type'] == 'success']
                if len(ack_ids) > 0:
                    hook.acknowledge(self.project, self.subscription, ack_ids)
                    return [msg for msg in self._messages if msg.get('ackId') and msg['ackId'] in ack_ids]


class SubscriptionTaskSet:

    def __init__(self, config, dag):
        self.config = config
        self.dag = dag

    @property
    def create_task(self):
        return PubSubSubscriptionCreateOperator(
            task_id='create_subscription', topic_project=self.config.project,
            subscription=self.config.subscription, topic=self.config.topic,
            subscription_project=self.config.subscription_project,
            dag=self.dag)

    @property
    def sensor_task(self):
        return CustomPubSubPullSensor(
            task_id='success_sensor',
            project=self.config.project,
            subscription=self.config.subscription,
            max_messages=2,
            ack_messages=True,
            dag=self.dag)

    @property
    def delete_task(self):
        return PubSubSubscriptionDeleteOperator(task_id='delete_subscription',
                                                project=self.config.project,
                                                subscription=self.config.subscription, dag=self.dag)
