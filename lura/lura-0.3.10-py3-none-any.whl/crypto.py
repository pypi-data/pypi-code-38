from cryptography.fernet import Fernet

def encrypt(data, key=None):
  key = Fernet.generate_key() if key is None else key
  fernet = Fernet(key)
  ciphertext = fernet.encrypt(data)
  del fernet
  return (ciphertext, key)

def decrypt(data, key):
  fernet = Fernet(key)
  plaintext = fernet.decrypt(data)
  del fernet, key
  return plaintext
