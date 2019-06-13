from .txt_when_done import txt_self, TxtWhenDoneMagics

name="txt_when_done"

try:
    ip = get_ipython()
    ip.register_magics(TxtWhenDoneMagics)
except:
    pass