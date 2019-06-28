from airflow import DAG
from airflow.contrib.operators.pubsub_operator import PubSubPublishOperator, PubSubTopicCreateOperator
from airflow.operators.subdag_operator import SubDagOperator
from airflow.contrib.operators.bigquery_operator import BigQueryOperator

from datetime import datetime
from event_triggering.config import config


def create_subdag_to_log_dag_state(project, main_dag_name, sub_dag_name, event_name, event_type):
    sub_dag = DAG('%s.%s' % (main_dag_name, sub_dag_name), catchup=False, max_active_runs=1,
                  start_date=datetime(2018, 3, 1))

    event_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    log_to_pubsub = PubSubPublishOperator(task_id='log-to-pubsub-' + event_name,
                                          project=project,
                                          topic=config.topic,
                                          gcp_conn_id=config.gcp_conn_name,
                                          messages=[{"attributes": {"dag_id": main_dag_name, "run_id": "{{ run_id }}",
                                                                   "event_timestamp": event_timestamp,
                                                                   "event_name": event_name,
                                                                   "event_type": event_type}}],
                                          dag=sub_dag)

    log_to_bq = BigQueryOperator(
        task_id="log-to-bq-" + event_name,
        bql="Select '"
        + main_dag_name
        + "' as dag_id, '{{ run_id }}' as run_id, timestamp('"
        + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        + "') as event_timestamp,'"
        + event_name
        + "' as event_name",
        destination_dataset_table=project + ".audit_dssor_daily.airflow_events",
        write_disposition="WRITE_APPEND",
        allow_large_results=False,
        bigquery_conn_id="google_cloud_default",
        use_legacy_sql=False,
        create_disposition="create_if_needed",
        dag=sub_dag,
    )

    return sub_dag


def create_start_subdag(dag_name, event_name, main_dag):
    return SubDagOperator(
        subdag=create_subdag_to_log_dag_state(config.project, dag_name, 'log_start_of_dag', event_name, 'start'),
        task_id='log_start_of_dag', dag=main_dag)


def create_success_subdag(dag_name, event_name, main_dag):
    return SubDagOperator(
        subdag=create_subdag_to_log_dag_state(config.project, dag_name, 'log_end_of_dag', event_name, 'success'),
        task_id='log_end_of_dag', dag=main_dag)


def log_task(dag, event_name, event_type):

    event_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    log_to_pubsub = PubSubPublishOperator(task_id='log-to-pubsub-' + event_name + '-' + event_type,
                                          project=config.project,
                                          topic=config.logging_topic,
                                          messages=[{"attributes": {"task_id": event_name, "run_id": "{{ run_id }}",
                                                                   "event_timestamp": event_timestamp,
                                                                   "event_type": event_type}}],
                                          dag=dag)

    if config.gcp_conn_name is not None:
        log_to_pubsub.gcp_conn_id = config.gcp_conn_name

    return log_to_pubsub


# For this function to work, the task passed can't have a previously assigned dag to it
def wrap_task_with_logging(task, task_name, main_dag_name):
    sub_dag = DAG('%s.%s' % (main_dag_name, task_name+"_dag"), catchup=False, max_active_runs=1,
                  start_date=datetime(2018, 3, 1), schedule_interval=None)

    topic_create = PubSubTopicCreateOperator(
        task_id='create-topic-' + task_name,
        project=config.project,
        topic=config.logging_topic,
        dag=sub_dag)
    log_start = log_task(sub_dag, task_name, 'start')
    log_success = log_task(sub_dag, task_name, 'success')

    task.dag = sub_dag

    topic_create >> log_start >> task >> log_success

    return sub_dag


def create_subdag_with_logging(task, task_name, main_dag, main_dag_name):

    sub_dag = wrap_task_with_logging(task, task_name, main_dag_name)

    return SubDagOperator(subdag=sub_dag, task_id=task_name+"_dag", dag=main_dag)


