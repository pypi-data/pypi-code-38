
import docker


def wait(target, port, network):

    print("Waiting for " + target)

    client = docker.from_env()

    waiter = client.containers.run(
        image="ubuntu:14.04",
        detach=True,
        name="wait_for_" + target,
        network=network.name,
        command=[
            "/bin/bash",
            "-c",
            """
            while ! nc -z {target} {port};
            do
                sleep 5;
            done;
            """.format(target=target, port=port),
        ]
    )

    waiter.wait()

    print(target + " is running")

    waiter.stop()
    waiter.remove()
