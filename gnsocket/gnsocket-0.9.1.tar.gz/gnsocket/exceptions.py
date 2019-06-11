def clean_exception(ex, gs, idc):
    gs.clean_client(idc)
    print("Socket Exception %s" % ex)


def raise_exception(ex, gs, idc):
    gs.clean_client(idc)
    raise ex
