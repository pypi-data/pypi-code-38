#!/usr/bin/env python3
import sys
import json
import glob
import progressbar
import mongoengine
import importlib
from pymongo import MongoClient
from subprocess import Popen, DEVNULL
from multiprocessing import Process


def write_config(config):

    # convert modules into importable format
    config["schemas"] = config["schemas"].rsplit(".", 1)[0].replace("/", ".")
    for program, handler in config["handlers"].items():
        config["handlers"][program] = handler.rsplit(".", 1)[0].replace("/", ".")

    with open("bin/config.py", "w") as file:
        file.write("config = " + str(config) + "\n")
        file.flush()


def write_instances(config, instances):
    schemas = importlib.import_module(config["schemas"])

    mongoengine.connect(config["database_name"], replicaset="monitoring_replSet")

    for instance in instances:
        stripped_instance = instance.split("/", 1)[1]

        if not schemas.Instance.objects(filename=stripped_instance):
            schemas.Instance.objects(filename=stripped_instance).\
                update_one(upsert=True, set__filename=stripped_instance)

    mongoengine.connection.disconnect()


def collect_handlers(config):

    handlers = {}

    for program in config["handlers"].items():
        cur_module = importlib.import_module(program[1])
        handlers[program[0]] = cur_module.output_handler

    return handlers


def monitor_database(config, num_instances, num_bench):
    commands = config["commands"]

    num_commands = 0
    for program in list(commands.values()):
        num_commands += len(list(program.values()))

    print("Running %d total commands\n" % (num_commands * num_instances * num_bench))

    client = MongoClient()
    db = client[config["database_name"]]

    with db.watch([{'$match': {'operationType': 'insert'}}]) as stream:

        for _ in progressbar.progressbar(range(num_commands * num_instances * num_bench)):
            stream.next()
            # print(stream.next()["fullDocument"])  TODO: possibly use for live-updating output


def main():

    config = json.loads(open(sys.argv[1], 'r').read())
    write_config(config)

    Popen("mongod --dbpath ./results --logpath ./results/log/mongodb.log".split() +
          " --replSet monitoring_replSet".split(), stdout=DEVNULL)

    num_bench = 1
    if len(sys.argv) > 2 and int(sys.argv[2]) >= 0:  # running bench 0 times just calls analyze
        num_bench = int(sys.argv[2])

    if num_bench != 0:

        instances = glob.glob("%s/**/*.*" % config["instances"], recursive=True)

        instance_writer = Process(target=write_instances, args=(config, instances))
        instance_writer.start()
        handlers = collect_handlers(config)
        instance_writer.join()

        database_monitor = Process(target=monitor_database, args=(config, len(instances), num_bench))
        database_monitor.start()

        from bin.bench import bench
        for _ in range(0, num_bench):
            bench(instances, handlers)

    from bin.analyze import analyze
    analyze()

    # TODO: find and kill any running mongod process


if __name__ == '__main__':
    main()
