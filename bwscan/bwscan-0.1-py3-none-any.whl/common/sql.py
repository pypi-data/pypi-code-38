from sqlalchemy import create_engine
from yaml import load as yload

# GCP imports
class GCPSQLAlchemy(object):
# ''' Google Cloud Platform MySQL connector for SQL Alchemy '''
 def __init__(self,cfg):
    self._connStr = None
    self._ssl = None
    #    if cfg is None: raise Exception("must be a valid json")
    self._parse_cfg(cfg)

 def _parse_cfg(self,cfg):
    cfg = yload(open(cfg,"r"))
    self._ssl = {'ssl':  {'cert':cfg.get("ssl_cert","NONE"),
                           'key':cfg.get("ssl_key","NONE"),
                            'ca':cfg.get("ssl_ca","NONE")
                        }
                }
    conn_string = '{user}:{password}@{host}:{port}/{database}'.format(
                                                                host=cfg.get("host","127.0.0.1"),
                                                                port = cfg.get("port","3306"),
                                                                user=cfg.get("user","NONE"),
                                                                password=cfg.get("password","NONE"),
                                                                database=cfg.get("database","NONE")
                                                             )
    self._connStr = 'mysql+pymysql://{conn_string}'.format(conn_string=conn_string)
 def updateSSL(self,key,value):
    self._ssl[key]=value

 def __repr__(self):
    return "GCP-SQLAlchemy Engine: %s"%self._connStr
 def createEngine(self,ssl=False):
    ''' use this method to return the sqlalchemy-compliant engine '''
    engine = create_engine(self._connStr,connect_args=self._ssl if ssl else {})
    return engine
