from Homevee.Exception import InvalidParametersException, AbstractFunctionCallException
from Homevee.Item import Item
from Homevee.Utils.Database import Database

PHILIPS_HUE_BRIDGE = "Philips Hue"
Z_WAVE_GATEWAY = "Z-Wave"
FUNKSTECKDOSEN_CONTROLLER = "Funksteckdosen-Controller"
MAX_CUBE = "MAX! Cube"
MQTT_BROKER = "MQTT Broker"
MIYO_CUBE = "MIYO Cube"
RADEMACHER_HOMEPILOT = "Rademacher HomePilot"


class Gateway(Item):
    def __init__(self, id, ip, port, key1, key2, type):
        super(Gateway, self).__init__()
        self.id = id
        self.ip = ip
        self.port = port
        self.key1 = key1
        self.key2 = key2
        self.type = type

    def save(self, db: Database = None):
        if db is None:
            db = Database()
        db.insert("""INSERT OR IGNORE INTO GATEWAYS (NAME, IP, PORT, KEY1, KEY2, TYPE) VALUES
                        (:name, :ip, :port, :key1, :key2, :type)""",
                        {'name': self.id, 'ip': self.ip, 'port': self.port,
                         'key1': self.key1, 'key2': self.key2, 'type': self.type})

        db.update("""UPDATE OR IGNORE GATEWAYS SET IP = :ip, PORT = :port, KEY1 = :key1,
                        KEY2 = :key2, TYPE = :type WHERE NAME = :name""",
                            {'ip': self.ip, 'port': self.port, 'key1': self.key1,
                         'key2': self.key2, 'type': self.type, 'name': self.id})

    def delete(self, db: Database = None):
        if db is None:
            db = Database()
        db.delete("DELETE FROM GATEWAYS WHERE NAME == :key", {'key': self.id})

    def build_dict(self):
        dict = {
            'name': self.id,
            'ip': self.ip,
            'port': self.port,
            'key1': self.key1,
            'key2': self.key2,
            'type': self.type
        }
        return dict

    @staticmethod
    def load_all_ids_from_db(ids, db: Database = None):
        if db is None:
            db = Database()
        return Gateway.load_all_from_db('SELECT * FROM GATEWAYS WHERE NAME IN (%s)' % ','.join('?' * len(ids)),
                                        ids, db)

    @staticmethod
    def load_all_from_db(query, params, db: Database = None):
        if db is None:
            db = Database()
        gateways = []
        for item in db.select_all(query, params):
            gateway = Gateway(item['NAME'], item['IP'], item['PORT'], item['KEY1'],
                              item['KEY2'], item['TYPE'])
            gateways.append(gateway)
        return gateways

    @staticmethod
    def create_from_dict(dict):
        try:
            name = dict['name']
            ip = dict['ip']
            port = dict['port']
            key1 = dict['key1']
            key2 = dict['key2']
            type = dict['type']

            gateway = Gateway(name, ip, port, key1, key2, type)

            return gateway
        except:
            raise InvalidParametersException("Invalid parameters for Gateway.create_from_dict()")

    def get_devices(self):
        raise AbstractFunctionCallException("Method Gateway.get_devices() is abstract")