""" Modified Launchpad class from FireWorks"""
from fireworks.core.launchpad import LaunchPad
from fireworks.fw_config import LAUNCHPAD_LOC


class LaunchPadHilde(LaunchPad):
    """
    The modified Launchpad that manges the FireWorks database
    """

    def __init__(self, *args, **kwargs):
        super(LaunchPadHilde, self).__init__(*args, **kwargs)

    def run_exists(self, fworker=None, ids=None):
        """
        Checks to see if the database contains any FireWorks of a given id set that are
        ready to run.

        Returns:
            bool: True if the database contains any FireWorks that are ready to run in a given set.
        """
        query = fworker.query if fworker else {}
        if ids:
            query["fw_id"] = {"$in": ids}
        return bool(self._get_a_fw_to_run(query=query, checkout=False))

    @classmethod
    def from_dict(cls, d):
        """
        Constructs a LaunchPad from a dict
        Args:
            cls: Class of the LaunchPad
            d: dict describing it
        """
        logdir = d.get("logdir", None)
        strm_lvl = d.get("strm_lvl", None)
        user_indices = d.get("user_indices", [])
        wf_user_indices = d.get("wf_user_indices", [])
        ssl = d.get("ssl", False)
        # ssl_ca_file was the old notation for FWS < 1.5.5
        ssl_ca_certs = d.get("ssl_ca_certs", d.get("ssl_ca_file", None))
        ssl_certfile = d.get("ssl_certfile", None)
        ssl_keyfile = d.get("ssl_keyfile", None)
        ssl_pem_passphrase = d.get("ssl_pem_passphrase", None)
        return LaunchPadHilde(
            d["host"],
            d["port"],
            d["name"],
            d["username"],
            d["password"],
            logdir,
            strm_lvl,
            user_indices,
            wf_user_indices,
            ssl,
            ssl_ca_certs,
            ssl_certfile,
            ssl_keyfile,
            ssl_pem_passphrase,
        )

    @classmethod
    def auto_load(cls):
        '''auto_load from default file'''
        if LAUNCHPAD_LOC:
            return LaunchPadHilde.from_file(LAUNCHPAD_LOC)
        return LaunchPadHilde()
