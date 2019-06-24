from dvcr.containers.base import BaseContainer
from dvcr.containers.postgres import Postgres

from docker.errors import ContainerError


class AirflowWorker(BaseContainer):
    def __init__(
        self,
        repo: str = "apache/airflow",
        tag: str = "master-3.6",
        name: str = "airflow",
        port: int = 8793,
        network=None,
        environment=None,
        dags_folder=None,
    ):
        super().__init__(repo=repo, tag=tag, name=name, port=port, network=network)

        self._container = self._client.containers.run(
            image=repo + ":" + tag,
            detach=True,
            name=name + "_worker",
            network=self._network.name,
            environment=environment,
            command=["worker"],
            volumes={dags_folder: {"bind": "/home/airflow/airflow/dags", "mode": "ro"}},
            ports={port: port},
        )


class AirflowScheduler(BaseContainer):
    def __init__(
        self,
        repo="apache/airflow",
        tag="master-3.6",
        port=8080,
        dags_folder=None,
        name="airflow",
        network=None,
        environment=None,
    ):
        super().__init__(network=network, port=port, repo=repo, name=name, tag=tag)

        self._container = self._client.containers.run(
            image=repo + ":" + tag,
            detach=True,
            name=name + "_scheduler",
            network=self._network.name,
            environment=environment,
            command=["scheduler"],
            ports={8080: 8081},
            volumes={dags_folder: {"bind": "/home/airflow/airflow/dags", "mode": "ro"}},
        )


class Airflow(BaseContainer):
    def __init__(
        self,
        repo="apache/airflow",
        tag="master-3.6",
        port=8080,
        dags_folder=None,
        backend=None,
        name="airflow",
        network=None,
        environment=None,
    ):
        """ Constructor for Airflow """
        super().__init__(network=network, port=port, repo=repo, name=name, tag=tag)

        self.use_default_backend = False

        if backend:
            self.backend = backend
        else:
            postgres_env = {
                "POSTGRES_USER": "airflow",
                "POSTGRES_PASSWORD": "airflow",
                "POSTGRES_DB": "airflow",
            }
            self.backend = Postgres(network=network, environment=postgres_env).wait()
            self.use_default_backend = True

        airflow_env = environment or {}

        if "AIRFLOW__CORE__SQL_ALCHEMY_CONN" not in environment:
            airflow_env[
                "AIRFLOW__CORE__SQL_ALCHEMY_CONN"
            ] = self.backend.sql_alchemy_conn()

        try:
            self.init_db(repo=repo, tag=tag, environment=airflow_env)
        except ContainerError as e:
            print(e.stderr.decode("utf8"))
            import sys

            sys.exit(1)

        self.create_admin_user(repo=repo, tag=tag, environment=airflow_env)

        self.scheduler = AirflowScheduler(
            repo=repo, tag=tag, environment=airflow_env, dags_folder=dags_folder
        )

        self._container = self._client.containers.run(
            image=repo + ":" + tag,
            detach=True,
            name=name + "_webserver",
            network=self._network.name,
            environment=airflow_env,
            command=["webserver"],
            ports={port: port},
            volumes={dags_folder: {"bind": "/home/airflow/airflow/dags", "mode": "ro"}},
        )

    def init_db(self, repo, tag, environment):

        self._client.containers.run(
            image=repo + ":" + tag,
            detach=False,
            name="airflow_initdb",
            network=self._network.name,
            environment=environment,
            command=["initdb"],
            auto_remove=True,
        )

    def create_admin_user(self, repo, tag, environment):

        self._client.containers.run(
            image=repo + ":" + tag,
            detach=False,
            name="airflow_create_user",
            network=self._network.name,
            environment=environment,
            command=[
                "users",
                "-c",
                "--username",
                "admin",
                "--password",
                "admin",
                "--role",
                "Admin",
                "--firstname",
                "admin",
                "--lastname",
                "admin",
                "--email",
                "admin@admin.com,",
            ],
            auto_remove=True,
        )

    def trigger_dag(self, dag):

        self.unpause_dag(dag)

        self.exec(cmd=["airflow", "trigger_dag", dag])

        return self

    def unpause_dag(self, dag):

        self.exec(cmd=["airflow", "unpause", dag])

    def delete(self):
        if self.use_default_backend:
            self.backend.delete()
        self.scheduler.delete()
        super(Airflow, self).delete()
