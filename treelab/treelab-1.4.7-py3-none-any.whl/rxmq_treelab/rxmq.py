from treelab.rxmq_treelab.channel import Channel


class Rxmq:
    """
    Rxmq, inspired by the js version lol
    """
    channels = {}

    @staticmethod
    def channel(name: str = 'defaultRxmqChannel') -> Channel:
        if name not in Rxmq.channels.keys():
            Rxmq.channels[name] = Channel()
        return Rxmq.channels[name]
