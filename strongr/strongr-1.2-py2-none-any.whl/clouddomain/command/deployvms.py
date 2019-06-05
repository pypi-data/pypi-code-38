class DeployVms(list):
    def __init__(self, names, profile, cores, ram):
        self.names = names
        self.profile = profile
        self.cores = cores
        self.ram = ram
