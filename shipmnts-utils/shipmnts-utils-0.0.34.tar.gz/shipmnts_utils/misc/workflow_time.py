import time
from shipmnts_utils.sql_executor import execute_select_query
from shipmnts_utils.redis_init import RedisConfig

redis = RedisConfig()
redis_client = redis.client

def calculate_workflow_time(job_id):
    auto_flow_time_spent, rerun_flow_time_spent = "0", "0"
    select_job_query = "SELECT message_id from jobs where id = {0} LIMIT 1".format(
        job_id
    )
    job = execute_select_query(select_job_query, fetch="one")
    auto_flow_start = fetch_time("auto_flow", job[0])
    rerun_auto_flow_start = fetch_time("rerun_flow", job[0])
    end_time = float(time.time())
    if auto_flow_start:
        start_time = float(auto_flow_start)
        auto_flow_time_spent = str(round(end_time - start_time, 4))
    if rerun_auto_flow_start:
        rerun_start_time = float(rerun_auto_flow_start)
        rerun_flow_time_spent = str(round(end_time - rerun_start_time, 4))
    return [auto_flow_time_spent, rerun_flow_time_spent]


def fetch_time(prefix, message_id):
    return redis_client.get("{0}_{1}".format(prefix, message_id))
