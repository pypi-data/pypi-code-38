from .codec._runner import _Codec
from .codec._schemer import infer as _infer
import json
import ast

def infer(samples):
    """
    Infer a schema from a list of examples
    """
    dicts = []
    other = []
    for s in samples:
        if isinstance(s, dict):
            dicts.append(s)
        else:
            other.append(s)

    df = _Codec(True)
    df.encoding = 2
    df.recordsets = True
    df.prepare_output()

    df_encoded = [ast.literal_eval(a) for a in df.encode(other) if a != '{"$fastscore": "set"}' and isinstance(a, str)]

    encoded = dicts + df_encoded

    return json.dumps(_infer(encoded), indent=4)