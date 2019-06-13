from termcolor import colored

empty = colored("\r\n[-] You must enter something! Try again!\n", 'red')

menu = colored("\r\n[-] You must select an option from menu ! Try again.\n", 'red')

value_type = colored("\r\n[-] Input values must be integers ! Try again.\n", 'red')

value = colored("\r\n[-] Input values need to be equal or greater than the default value! Try again.\n", 'red')

value_empty = colored("\r\n[-] You must enter a password ! Try again.\n", 'red')

aes_key_size = colored("\r\n[-] You must enter 128, 192 or 256! Try again.\n", 'red')

aes_modes = colored("\r\n[-] You must enter CBC or CTR! Try again.\n", 'red')

aes_iv = colored("\r\n[-] Not valid! You must enter a initialization vector!\n", 'red')

aes_empty = colored("\r\n[-] You must enter a text to encrypt ! Try again.\n", 'red')

rsa_key_size = colored("\r\n[-] You must enter 1024, 2048 or 4096! Try again.\n", 'red')

dsa_key_size = colored("\r\n[-] You must enter 1024, 2048 or 3072! Try again.\n", 'red')

ecdsa_key_size = colored("\r\n[-] You must enter 224, 256, 384 or 521! Try again.\n", 'red')

sha_key_size = colored("\r\n[-] You must enter 224, 256, 384 or 521! Try again.\n", 'red')

gpg_key_size = colored("\r\n[-] You must enter 1024 or 2048! Try again.\n", 'red')

gpg_invalid_email = colored("\r\n[-] Not valid! Email address does not exists!\n", 'red')

gpg_no_passphrase = colored("\r\n[-] Not valid! You must enter a passphrase!\n", 'red')

gpg_invalid_key = colored("\r\n[-] Non existing GPG key or wrong passphrase! Try again!\n", 'red')

gpg_invalid_query = colored("\r\n[-] You must enter something! Try again!\n", 'red')

gpg_invalid_key_type = colored("\r\n[-] RSA or DSA algorithm! Try again!\n", 'red')

gpg_no_import = colored('\n GPG Key NOT imported! Key must have a problem!\n', 'red')

gpg_no_deleted = colored('\n GPG Key NOT deleted! Key must have a problem!\n', 'red')

gpg_key_list = colored('\n GPG Key list empty!\n', 'red')

gpg_no_key = colored('GPG Key not found!\n', 'red')

gpg_no_encrypt = colored('\n Text could not be encrypted!\n', 'red')

gpg_no_decrypt = colored('\n Text could not be decrypted!\n', 'red')

gpg_no_sign = colored('\n Text could not be signed!\n', 'red')

gpg_no_verify = colored('\n Signature could not be verified!\n', 'red')

gpg_no_expdate = colored('\n Not valid! Specify an expiration date!\n', 'red')

x509_modes = colored("\r\n[-] You must enter RSA, DSA or ECDSA! Try again.\n", 'red')
