class ContractMetaData:
    def __init__(self, web3, asyncexec, address, abi, signer=None):
        self.web3 = web3
        self.asyncexec = asyncexec
        self.address = address
        self.abi = abi
        self.signer = signer
