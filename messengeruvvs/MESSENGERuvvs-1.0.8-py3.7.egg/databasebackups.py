"""Backup data in MESSENGER database tables."""
import os


def databasebackups(database='thesolarsystemmb'):
    # Read in current config file if it exists
    configfile = os.path.join(os.environ['HOME'], '.nexoclom')
    config = {}
    if os.path.isfile(configfile):
        for line in open(configfile, 'r').readlines():
            key, value = line.split('=')
            config[key.strip()] = value.strip()
        if database in config:
             database = config['database']
        else:
            pass
    else:
        assert 0, 'Data path is not defined.'

    mestables = ['capointing', 'cauvvsdata', 'mesmercyear', 'mgpointing',
              'mguvvsdata', 'napointing', 'nauvvsdata']

    for table in mestables:
        print(f'Backing up {table}')
        savef = os.path.join(config['datapath'], f'UVVS_{table}.sql')
        os.system(f"pg_dump -t {table} {database} > {savef}")

if __name__ == '__main__':
    databasebackups()
