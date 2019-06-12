from bitshares.asset import Asset as BitsharesAsset

class Asset(BitsharesAsset):
    def __init__(
        self,
        asset,
        lazy=False,
        full=False,
        cybex_instance =None
    ):
        super(Asset, self).__init__(asset = asset, lazy = lazy,
            full = full, bitshares_instance = cybex_instance)
