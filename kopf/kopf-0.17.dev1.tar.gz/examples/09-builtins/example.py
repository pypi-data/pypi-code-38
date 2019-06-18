import asyncio

import kopf
import pykube

TIMEOUT = 30
tasks = {}  # dict{namespace: dict{name: asyncio.Task}}


@kopf.on.resume('', 'v1', 'pods')
@kopf.on.create('', 'v1', 'pods')
async def pod_in_sight(namespace, name, logger, **kwargs):
    if namespace.startswith('kube-'):
        return
    else:
        task = asyncio.create_task(pod_killer(namespace, name, logger))
        tasks.setdefault(namespace, {})
        tasks[namespace][name] = task


@kopf.on.delete('', 'v1', 'pods')
async def pod_deleted(namespace, name, **kwargs):
    if namespace in tasks and name in tasks[namespace]:
        task = tasks[namespace][name]
        task.cancel()  # it will also remove from `tasks`


async def pod_killer(namespace, name, logger):
    try:
        logger.info(f"=== Pod killing happens in {TIMEOUT}s.")
        await asyncio.sleep(TIMEOUT)
        logger.info(f"=== Pod killing happens NOW!")

        api = kopf.get_pykube_api()
        pod = pykube.Pod.objects(api, namespace=namespace).get_by_name(name)
        pod.delete()

    except asyncio.CancelledError:
        logger.info(f"=== Pod killing is cancelled!")

    finally:
        if namespace in tasks and name in tasks[namespace]:
            del tasks[namespace][name]
