from . import cpu, ram


def statistics():
    return {'cpu': cpu.statistics(),
            'ram': ram.statistics()
            }
