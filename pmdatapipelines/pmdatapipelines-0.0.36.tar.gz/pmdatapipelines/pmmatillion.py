import boto3
import json
from botocore.exceptions import ClientError


def run_job(job_name):

	message = {
		"group":"pm-editorial",
		"project":"pm-editorial-dev",
		"version":"default",
		"environment":"pm-editorial-dev"
	}

	message['job'] = job_name

	print(message)
	
	sqs_res = boto3.resource("sqs")
	queue = sqs_res.get_queue_by_name(QueueName='TriggerMatillionJobs')
	response = queue.send_message(
		MessageBody=json.dumps(message)
	)
	print(response)