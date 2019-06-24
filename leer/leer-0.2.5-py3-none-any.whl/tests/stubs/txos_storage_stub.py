class TXOsStorageStub():

  class Interface:

    def __init__(self):
      self.storage = {}

    def __getitem__(self, hash_and_pc):
      if not hash_and_pc in self.storage:
        raise KeyError(hash_and_pc)
      return self.storage[hash_and_pc]

    def __setitem__(self, hash_and_pc, utxo):
      #here we should save
      self.storage[hash_and_pc]=utxo

    def __contains__(self, utxo):
      return utxo in self.storage  

  def __init__(self):
    self.confirmed = self.Interface()
    self.mempool = self.Interface()


