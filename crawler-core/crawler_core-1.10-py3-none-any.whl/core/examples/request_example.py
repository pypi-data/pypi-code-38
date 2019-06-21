from core import Database
from core import Proxies
from core import Request

_url = 'https://check.torproject.org/'

tor_view = 'v_tor_list'
proxy_viev = 'v_proxy_list'

# creating database session
Database.db_type = 'ms'
database_config = r'C:\Users\draganm\Documents\database.config'
db = Database(database_config, 1)

# we ca start an instance of Proxies of two types
# ==============================================
# ============== TOR EXIT NODES ================
# ==============================================
# will aquire a list of tor's from view over database session
proxies = Proxies(db, tor_view, hostip='ipv4')


# ==============================================
# ============== PUBLIC PROXIES ================
# ==============================================
# or it will aquire a list of public proxies from view over database sessionž
# default columns ov view are ip, port if you called them differently use
# args ipname and/or portname
proxies = Proxies(db, proxy_viev, ipname='proxy_ip', portname='proxy_port')


# ==============================================
# ================= GET EXAMPLE ================
# ==============================================

# this part creates requests session
r = Request()
# here we select what kind of request we are doing 2=get with proxies
r.request_type = 2
# here we set proxy for this instance of request
r = proxies.set_proxy(r, 0)
# go method makes request twoards the page
r.go(_url)
# final result is returned in BeautifulSoup
html_bs = r.response.content

# if an error occured it will be dictionary
if type(html_bs) is dict:
    print("error occurred: {}".format(html_bs.get('RequestError')))
    exit()

# ==============================================
# ================= CHANGE TOR  ================
# ==============================================
# new session
r = Request()
# select request type
r.request_type = 2
# change tor
r = proxies.set_proxy(r, 0, new=True)
# REST IS SAME AS GET EXAMPLE


# ==============================================
# ================= POST EXAMPLE ===============
# ==============================================

# create session
r = Request()
# request type to 4=post with proxies 3 without proxies
r.request_type = 4
# add payload data aka post data
payload = {'google-token': 'dhlfanp', 'search': 'python'}
r.payload = payload
# REST IS SAME AS GET EXAMPLE