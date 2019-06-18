#!/usr/bin/python3.6
from confluent_kafka import avro
import urllib.request
import json
import psycopg2
from confluent_kafka import Consumer, KafkaException, KafkaError
import confluent_kafka
import avro.schema
import avro.io
import io
import os
import sys
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import Producer
import fcntl
import argparse

is_debug_log  = False
is_info_log = False

conf_dict = {}

def read_py_conf():
    info_log('read_py_conf() called, line 24')
    with open("conf.cnf") as f:
        config = f.readlines()
    debug_log('read_py_conf(), line 27')
    config = [x.strip() for x in config]
    info_log('Your config is: ' + str(config))
    return config

def read_schema(config):
    info_log('read_schema(config) called, line 31')
    # jsondata = json.load(urllib.request.urlopen(config[0]))
    # schema = avro.schema.Parse(str(jsondata['schema']))
    debug_log('read_schema(config), line 36')
    schema = avro.schema.Parse("""{
      "namespace" : "my.com.ns",
      "name": "myrecord",
      "type" :  "record",
      "fields" : [
         {"name": "uid", "type": "int"},
         {"name": "somefield", "type": "string"},
         {"name": "options", "type": {
            "type": "array",
            "items": {
                "type": "record",
                "name": "lvl2_record",
                "fields": [
                    {"name": "hel", "type": "string"}
                ]
            }
         }}
      ]
    }""")
    return schema

def set_up_conf_dict(cur):
    info_log('set_up_conf_dict(cur) called, line 56')
    cur.execute("""SELECT * FROM config_table""")
    rows = cur.fetchall()
    debug_log('set_up_conf_dict(cur), line 62')
    for row in rows:
       conf_dict[row[0]] = row[1]
    
    cur.execute("""SELECT DISTINCT(topic_name) FROM topic_field_map""")
    rows = cur.fetchall()
    debug_log('set_up_conf_dict(cur), line 68')
    conf_dict['new_topics'] = []
    for row in rows:
       conf_dict['new_topics'].append(row[0])
    debug_log('set_up_conf_dict(cur), line 72')
    conf_dict['data_for_new_topics'] = []
    for t in conf_dict['new_topics']:
        cur.execute("""SELECT field_name FROM topic_field_map WHERE topic_name='{}'""".format(t))
        conf_dict['data_for_new_topics'].append([str(item)[2:-3] for item in cur.fetchall()])

def write_to_topic(topic, rec, cur):
    info_log('write_to_topic(topic, rec, cur) called, line 75')
    p = Producer({'bootstrap.servers': conf_dict['bootstrap_server_to']+conf_dict['bootstrap_server_to_port']})
    p.produce(topic, str.encode(str(rec)))
    debug_log('write_to_topic(topic, rec, cur), line 82')
    p.flush()

def to_csv(text,rec):
    info_log('to_csv(text,rec) called, line 81')
    result = ""
    temp_str = text.split(',')
    for t in temp_str:
        try:
            if(len(t.split(' '))>1):
                arr = t.split(' ')
                debug_log('to_csv(text,rec), line 93')
                result+=str(rec[arr[0]][0][arr[1]])
                result+=','
            else:
                result+=str(rec[t])
                debug_log('to_csv(text,rec), line 98')
                result+=','
        except Exception:
            result+=','
            continue
    return result[:-1]

def on_assign (c, ps):
    info_log('on_assign (c, ps) called, line 99')
    if conf_dict['from_beginning']=='1' and os.path.getsize("./binary_avro_consumer.temp")==0:
        f=open("binary_avro_consumer.temp","a")
        f.write('1')
        for p in ps:
            p.offset=confluent_kafka.OFFSET_BEGINNING   
        c.assign(ps)
    else:
        for p in ps:
            p.offset=confluent_kafka.OFFSET_INVALID   
        c.assign(ps)

def consume(conf_dict, cur, config):
    info_log('consume(conf_dict, cur, config) called, line 109')
    conf = {'bootstrap.servers': conf_dict['bootstrap_server_from']+':'+conf_dict['bootstrap_server_from_port'],
            'group.id': conf_dict['group_id']
            }
    c = Consumer(**conf)
    c.subscribe([conf_dict['topic_read']],on_assign=on_assign)
    schema = read_schema(config)
    running = True
    debug_log('consume(conf_dict, cur, config), line 124')
    msg_list = []
    while running:
        msg_list = c.consume(num_messages=int(conf_dict['count_messages_consume']),timeout=1.0)
        for msg in msg_list:
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                    (msg.topic(), msg.partition(),
                                       msg.offset()))
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                sys.stderr.write('%% %s [%d] at offset %d with key :\n' %
                                  (msg.topic(), msg.partition(), msg.offset(),))
            debug_log('consume(conf_dict, cur, config), line 139')
            message = msg.value()
            bytes_reader = io.BytesIO(message)
            decoder = avro.io.BinaryDecoder(bytes_reader)
            reader = avro.io.DatumReader(schema)
            try:
                record = reader.read(decoder)
                for t,records in zip(conf_dict['new_topics'],conf_dict['data_for_new_topics']):
                    ready = ""
                    debug_log('consume(conf_dict, cur, config), line 148')
                    for r in records:
                        ready+=to_csv(r+',',record)
                    ready = ready[:-1]
                    write_to_topic(t,ready,cur)
                sys.stdout.flush()
            except AssertionError:
                continue
                
    print("Shutting down consumer..")
    c.close()

def debug_log(str_msg):
    global is_debug_log
    if(is_debug_log):
        print('[DEBUG] ' + str_msg)

def info_log(str_msg):
    global is_info_log
    if(is_info_log):
        print('[INFO] ' + str_msg)

def main(args):
    if args is not None:
        if args.remove:
            try:
                os.remove('./binary_avro_consumer.temp')
            except OSError:
                pass
    f=open("binary_avro_consumer.temp","a")
    info_log('main(args) called, line 161')
    global is_debug_log
    is_debug_log = args.debug
    global is_info_log
    is_info_log = args.info
    debug_log('main(args), line 176')
    fh=open('binary_avro_consumer_lock.temp','a')
    try:
        fcntl.flock(fh,fcntl.LOCK_EX|fcntl.LOCK_NB)
        config = read_py_conf()
        conn = psycopg2.connect(dbname=config[1],user=config[2],password=config[3],host=config[4])
        cur = conn.cursor()
        set_up_conf_dict(cur)
        debug_log('main(args), line 184')
        consume(conf_dict, cur, config)
        conn.close()
    except KeyboardInterrupt:
        print('Keyboard interrupt!')
    except:
        print('The instance of script exists in memory!\nos._exit(0)')
        os._exit(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Kafka avro binary consumer")
    parser.add_argument('-d','--debug', action='store_true', help="Debug log mode")
    parser.add_argument('-i','--info', action='store_true', help="Info log mode")
    parser.add_argument('-r','--remove', action='store_true', help="Remove temp file")

    main(parser.parse_args())
