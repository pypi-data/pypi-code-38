# top-level script environment
# defined when running python -m mphops
from socks5_ipv8.mphops import start_proxy

if __name__ == "__main__":
    # execute only if run as a script
    start_proxy.main()
