import dockerdb.service


# docker pull influxdb:1.5.4
class InfluxDB(dockerdb.service.HTTPServer):
    name = 'influxdb'
    port = 8086

    def __init__(self, tag, wait=False, exposed_port=None, **kwargs):
        """

        * port - expose database to host on `port`
        * wait - if true the call blocks until MongoDB is ready to accept clients
        """
        self.exposed_port = exposed_port

        ports = {}
        if exposed_port:
            container_port = '{}/tcp'.format(self.port)
            ports[container_port] = ('127.0.0.1', exposed_port)
        super(InfluxDB, self).__init__('influxdb:' + tag, ports=ports, **kwargs)

    def factory_reset(self):
        """factory reset the database"""
        raise NotJetImplemented()
