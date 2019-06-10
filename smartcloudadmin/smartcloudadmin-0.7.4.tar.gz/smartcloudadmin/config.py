import logging


class BssConfig:

    log_level = logging.ERROR

    default_environment = ""

    verify_ssl = True

    datacenters = {}

    def add_datacenter(self, env_name: str, env_url: str, env_username_password: (str, str)):
        """
            Makes more sense to call them datacenter
        :return:
        """
        self.datacenters[env_name] = {
            "url": f"{env_url}",
            "auth": env_username_password
        }




    def get_credentials(self, env_name: str):
        return self.datacenters.get(env_name).get("auth")

    def get_url(self, env_name: str):
        return self.datacenters.get(env_name).get("url")
