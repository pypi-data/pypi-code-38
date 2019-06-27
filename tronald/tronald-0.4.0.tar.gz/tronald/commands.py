import os


def build_postgres_dump(config):
    return "docker exec -t {} pg_dump {} -c -U {}".format(
        config.container, config.db_name, config.postgres_user
    )


def remove_remote_dump(config):
    return "rm {}".format(config.dump_name)


def import_dump_to_local_container(
    dump_path, container_identifier, postgres_user, postgres_db
):
    command = "cat {} | docker exec -i {} psql -U {} --dbname {}".format(
        dump_path, container_identifier, postgres_user, postgres_db
    )
    return os.system(command)

