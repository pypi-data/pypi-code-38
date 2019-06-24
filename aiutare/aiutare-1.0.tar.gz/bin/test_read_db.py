import mongoengine
import importlib

from bin.config import config
schemas = importlib.import_module(config["schemas"])


def main():
    mongoengine.connect(config["database_name"], replicaset="monitoring_replSet")
    print("%d Instances found" % len(schemas.Instance.objects()))
    print("%d Results found" % len(schemas.Result.objects()))

    for Instance in schemas.Instance.objects():
        print(Instance.to_json())

    for Result in schemas.Result.objects():
        print(Result.to_json())

    mongoengine.connection.disconnect()


if __name__ == '__main__':
    main()
