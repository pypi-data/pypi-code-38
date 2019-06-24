from bluemax.utils.config import load_config
from tornado.options import define, options

define("debug", type=bool, default=True, help="auto reload etc")
define("port", type=int, default=8080, help="port to listen on")
define("workers", type=int, default=1, help="number of worker threads")
define("procedures", type=str, default="", help="procedures to make available")
define("services", type=str, default="", help="services to make available")
define("static_dir", type=str, default=None, help="static web directory")
define("redis_url", default="", help="redis url")
define("redis_work_q", default="_work_q_", help="name of queue to rpush to")

define("cookie_name", type=str, default="bluemax", help="bluemax session cooklie name")
define(
    "cookie_secret",
    type=str,
    default="it was a dark and stormy night, blue max",
    help="session secret",
)
define("login_url", type=str, default="/login", help="url for login")
define("auth_class", type=str, default=None, help="class of login handlers")

define("ms_app_id", type=str, help="MS App ID for authentication")
define("ms_app_secret", type=str, help="MS App Secret for authentication")

define("settings_extend", type=str, help="fully qualified function to import and call")
define("urls_extend", type=str, help="fully qualified function to import and call")
define("log_extend", type=str, help="fully qualified function to import and call")


def settings():
    result = {
        "cookie_secret": options.cookie_secret,
        "login_url": options.login_url,
        "debug": options.debug,
    }
    return result
