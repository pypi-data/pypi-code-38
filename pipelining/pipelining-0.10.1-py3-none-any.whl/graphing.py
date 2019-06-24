from .structure import Pipeline

def __yield_nodes(pipeline: Pipeline):
    for name, _ in pipeline.stages.items():
        yield dict(v=name)

def __yield_edges(pipeline: Pipeline):
    for _, queue in pipeline.queues.items():
        for producer in queue.producers:
            for consumer in queue.consumers:
                v = producer.owner.name
                w = consumer.owner.name
                yield dict(name=queue.name, v=v, w=w)
        

def build_pipeline_graph(pipeline: Pipeline):
    nodes = list(__yield_nodes(pipeline))
    edges = list(__yield_edges(pipeline))
    return dict(
        nodes=nodes,
        edges=edges
    )