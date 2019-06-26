import paramtools
class ExtParams(paramtools.Parameters):
    defaults = "extend_ex.json"
    array_first = True
    label_to_extend = "d0"

params = ExtParams()
params.set_state(d0=3)
params.adjust({"extend_param": [{"d0": 2, "value": 5}]})

