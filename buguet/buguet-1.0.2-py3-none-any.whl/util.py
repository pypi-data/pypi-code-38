import json

def ppp(x):
    print(json.dumps(x, default=lambda o: {**o.__dict__, 'type': type(o).__name__ }, sort_keys=True, indent=4))
