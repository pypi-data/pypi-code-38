import boto3
import logging
import json

def format_message_body(message):
    '''Helper function that will JSONIFY a message
    used to structure tested payload data manually 
    put into SQS queus in AWS'''
    if type(message) == unicode or type(message) == str:
        #print('Incoming SQS message is stringy, attempting to JSONIFY')
        message_json = json.loads(message) 
    else:
        message_json = message
    #print('Post adj payload type: %s' % type(message_json))
    return message_json

def parse_body_from_sqs_payload(item):
    '''Takes the message body out of either SQS or SNS, trying to keep options open'''
    try:
        message_body = item['body'] #for SQS
    except KeyError:
        message_body = item['Sns']['Message'] #for SNS
    return format_message_body(message_body)

def send_batch(message_list, queue_url):
    '''Invoke SQS and send'''
    sqs = boto3.client('sqs')
    chunk_size = 10 #boto3 limit
    logging.info("Sending size %s chunks" % chunk_size)
    logging.debug("Outbound SQS queue url: %s" % queue_url )
    for chunk in _chunk_list(message_list, chunk_size):
        logging.debug("Sending SQS chunk: %s" % chunk )
        result = sqs.send_message_batch(
            QueueUrl=queue_url,
            Entries=_structure_sqs_payload(chunk)
            )
        logging.info(result)

def _chunk_list(my_list, chunk_size): 
    ''' Break {my_list} into chunks of size {chunk_size}'''
    for i in range(0, len(my_list), chunk_size):  
        yield my_list[i:i + chunk_size] 

def _structure_sqs_payload(my_list):
    ''' This will structure a list of records for SQS bulk send '''
    sqs_records = []
    id = 0
    for item in my_list:
        record = {
                "Id": str(id),
                "MessageBody": str(item)
            }
        sqs_records.append(record)
        id = id + 1
    return sqs_records