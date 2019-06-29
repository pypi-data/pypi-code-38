if __name__ == "__main__":
    import sys
    import os
    from mud_engine import MUDEngine
    import logging
    logging.basicConfig(level=logging.DEBUG)
    host = "127.0.0.1" if not (len(sys.argv) > 2 and sys.argv[1]) else sys.argv[1]
    port = 5000 if not (len(sys.argv) > 2 and sys.argv[2]) else sys.argv[2]
    mud = MUDEngine(host, int(port))
    mud.admins.append(os.environ.get('ADMIN', 'ben'))
    mud.run()
    sys.exit(0)
