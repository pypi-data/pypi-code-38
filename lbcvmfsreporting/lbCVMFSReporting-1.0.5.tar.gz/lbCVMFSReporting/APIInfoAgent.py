from pyrabbit2.api import Client
import os


class APIInfoAgent():

    def __init__(self):
        user, pwd = self._get_pwd_from_sys()
        self.cl = Client('lbmessagingbroker.cern.ch:15672',
                         user, pwd)
        assert self.cl.is_alive() is True

    def _get_pwd_from_sys(self):
        """
        Get the RabbitMQ password from the environment of from a file on disk
        """
        # First checking the environment
        res = os.environ.get("RMQPWD", None)

        # Checking for the password in $HOME/private/rabbitmq.txt
        if res is None:
            fname = os.path.join(os.environ["HOME"], "private", "rabbitmq.txt")
            if os.path.exists(fname):
                with open(fname, "r") as f:
                    data = f.readlines()
                    if len(data) > 0:
                        res = data[0].strip()

        # Separate the username/password
        (username, password) = res.split("/")
        return username, password

    def sizeof_fmt(self, num, suffix='B'):
        for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)

    def getMemory(self):
        nodes = self.cl.get_nodes()
        toReturn = {'summary': [], 'details': {}, 'total':{}}
        for node in nodes:
            toReturn['summary'].append({
                'name': node['name'],
                'memory_limit': self.sizeof_fmt(node['mem_limit']),
                'memory_usage': self.sizeof_fmt(node['mem_used']),
                'memory_alert': node['mem_alarm'],
            })
        t_message_memory_usage = 0
        t_memory_usage = 0
        for host in self.cl.get_vhost_names():
            toReturn['details'][host] = {}
            for queue in self.cl.get_queues(host):
                toReturn['details'][host][queue['name']] = {
                    'message_memory_usage': self.sizeof_fmt(
                        queue['message_bytes_ram']),
                    'memory_usage': self.sizeof_fmt(queue['memory']),
                }
                t_message_memory_usage += queue['message_bytes_ram']
                t_memory_usage += queue['memory']
        toReturn['total'] = {
            'message_memory_usage': self.sizeof_fmt(t_message_memory_usage),
            'memory_usage': self.sizeof_fmt(t_memory_usage),
        }
        return toReturn

    def getNumberOfDevActions(self):
        q = self.cl.get_queue('/lhcb', 'CVMFSDevActions')
        return {
            'message_memory_usage': self.sizeof_fmt(q['message_bytes_ram']),
            'messages_disk_usage': self.sizeof_fmt(
                q['message_bytes_persistent']),
            'memory_usage': self.sizeof_fmt(q['memory']),
            'total_nb_messages': q['messages'],
            'nb_messages_on_disk': q['messages_persistent'],
            'nb_messages_on_ram': q['messages_ram']
        }

    def getDisplayForReport(self):
        msg = ['Summary of RabbitMQ usage:']
        mem = self.getMemory()
        dAct = self.getNumberOfDevActions()
        msg.append("\tTotal nb of actions in queue: %s (Memory usage: %s)" % (
            dAct['total_nb_messages'],
            dAct['memory_usage']
        ))
        msg.append("\tTotal memory in use: %s (limit at %s)" % (
            mem['summary'][0]['memory_usage'],
            mem['summary'][0]['memory_limit']))
        msg.append('')
        status = "Normal"
        if dAct['total_nb_messages'] > 750:
            status = 'Warning'
        if dAct['total_nb_messages'] > 1200:
            status = 'Danger'
        msg.append("Behaviour evaluation: %s" % status)
        msg.append('')
        return msg

    def getInfoForReport(self):
        toReturn = {
            'total_nb_messages': None,
            'memory_nb_usage': None,
            'memory_usage': None,
            'memory_limit': None,
            'evaluation': None
        }

        mem = self.getMemory()
        dAct = self.getNumberOfDevActions()

        toReturn['total_nb_messages'] = dAct['total_nb_messages']
        toReturn['memory_nb_usage'] = dAct['memory_usage']
        toReturn['memory_usage'] = mem['summary'][0]['memory_usage']
        toReturn['memory_limit'] = mem['summary'][0]['memory_limit']
        status = "Normal"
        if dAct['total_nb_messages'] > 750:
            status = 'Warning'
        if dAct['total_nb_messages'] > 1200:
            status = 'Danger'
        toReturn['evaluation'] = status
        return toReturn
