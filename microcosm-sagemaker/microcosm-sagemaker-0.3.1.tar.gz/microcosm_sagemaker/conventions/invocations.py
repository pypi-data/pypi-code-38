"""
Invocations controller.

"""
from microcosm_flask.conventions.saved_search import configure_saved_search
from microcosm_flask.namespaces import Namespace
from microcosm_flask.operations import Operation


def configure_invocations(graph, definition):
    """
    Define the invocations endpoint required by Sagemaker

    """
    # NB: The `SavedSearch` operation is used when we want to support a
    # `search` endpoint that expects a `POST` instead of a `GET`.  In our case,
    # we don't actually save the search in any way.
    graph.config.swagger_convention.operations.append("saved_search")
    ns = Namespace(
        subject="invocations",
        version=None,
    )
    mappings = {
        Operation.SavedSearch: definition,
    }
    configure_saved_search(graph, ns, mappings)

    return ns
