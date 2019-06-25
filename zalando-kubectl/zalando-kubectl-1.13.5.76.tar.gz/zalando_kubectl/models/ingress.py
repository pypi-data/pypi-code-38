import json

RAW_WEIGHTS_ANNOTATION = 'zalando.org/backend-weights'
STACKSET_WEIGHTS_ANNOTATION = 'zalando.org/stack-traffic-weights'


def parse_backend_weights(all_backends, current_weights):
    if current_weights:
        weights = {backend: weight for backend, weight in current_weights.items()}
    else:
        weights = {backend: 1 for backend in all_backends}

    return {backend: max(0.0, weights.get(backend, 0.0)) for backend in all_backends}


def parse_annotations(annotations_obj: dict, stackset_backends, raw_backends):
    raw_weights_str = annotations_obj.get(RAW_WEIGHTS_ANNOTATION, '{}')
    raw_weights = parse_backend_weights(raw_backends, json.loads(raw_weights_str))
    stackset_weights_str = annotations_obj.get(STACKSET_WEIGHTS_ANNOTATION, '{}')
    stackset_weights = parse_backend_weights(stackset_backends, json.loads(stackset_weights_str))
    return raw_weights, stackset_weights


class Ingress:
    def __init__(self, kubernetes_obj, stackset_backends, raw_backends, stackset_managed):
        self.name = kubernetes_obj['metadata']['name']
        self.stackset_backends = stackset_backends
        self.raw_backends = raw_backends
        self.stackset_managed = stackset_managed
        self.raw_weights, self.stackset_weights = parse_annotations(kubernetes_obj['metadata'].get('annotations', {}),
                                                                    stackset_backends, raw_backends)

    @property
    def annotation(self):
        if self.stackset_managed:
            return STACKSET_WEIGHTS_ANNOTATION
        else:
            return RAW_WEIGHTS_ANNOTATION

    @property
    def weights(self):
        if self.stackset_weights:
            return self.stackset_weights
        else:
            return self.raw_weights

    def set_weight(self, host: str, weight: float, force=False):
        if not self.stackset_managed and host not in self.raw_backends:
            raise RuntimeError("Backend {} missing in ingress {}".format(host, self.name))

        if self.stackset_managed and host not in self.stackset_backends:
            raise RuntimeError("Stack {} missing in stackset {}".format(host, self.name))

        new_weights = {host: weight}

        # Redistribute the remaining weights
        remaining_weight = 100.0 - weight
        total_remaining_weight = sum(weight for b, weight in self.weights.items() if b != host)

        if self.stackset_managed:
            if total_remaining_weight == 0 and weight != 100.0:
                errmsg = "The only active backend {} should receive all the traffic, must be 100"
                raise ValueError(errmsg.format(host))
        else:
            if total_remaining_weight == 0 and weight not in (0.0, 100.0):
                errmsg = "The only active backend {} cannot get partial traffic, must be either 0 or 100."
                raise ValueError(errmsg.format(host))

        for backend, weight in self.weights.items():
            if backend != host:
                new_weights[backend] = 0.0 if weight == 0.0 else round(
                    weight * remaining_weight / total_remaining_weight, 1)

        if self.stackset_managed:
            self.stackset_weights = new_weights
        if not self.stackset_managed or force:
            self.raw_weights = new_weights
