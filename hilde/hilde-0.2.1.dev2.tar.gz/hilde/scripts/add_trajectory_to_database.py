from argparse import ArgumentParser

from hilde.settings import Settings
from hilde.phonon_db.database_interface import traj_to_database

def main():
    parser = ArgumentParser(description="add trajectory to a database")
    parser.add_argument("trajectory", type=str, help="the trajectory file")
    parser.add_argument("db_path", type=str, default=None, help="Path to the database")
    args = parser.parse_args()
    if not args.db_path:
        settings = Settings()
        arg.db_path = settings.database.name
    hashes = traj_to_database(args.db_path, args.trajectory, True)
    print(hashes)