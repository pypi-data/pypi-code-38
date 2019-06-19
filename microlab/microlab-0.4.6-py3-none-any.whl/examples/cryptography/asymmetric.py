from microlab.cryptography.asymmetric import AsymmetricCryptography
from microlab.io.folders import delete_folder
from microlab.io.files import create_file
import os

if __name__ == '__main__':
    print('\n ~ TEST ASYMETRIC CRYPTOGRAPHY')
    pk_folder = os.path.join(os.getcwd(), 'private')
    pbk_folder = os.path.join(os.getcwd(), 'public')
    originals = os.path.join(os.getcwd(), 'originals')
    encrypted = os.path.join(os.getcwd(), 'encrypted')
    decrypted = os.path.join(os.getcwd(), 'decrypted')

    asymmetric = AsymmetricCryptography(private_keys_folder=pk_folder,
                                        public_keys_folder=pbk_folder,
                                        originals_folder=originals,
                                        encrypted_folder=encrypted,
                                        decrypted_folder=decrypted)

    create_file(path=os.path.join(originals, 'a.txt'), data=b'encrypt me!', verbose=True)
    asymmetric.generate_pair_of_keys(key_size=2048, verbose=True)
    asymmetric.export_private_key(key_name='private_key.pem', verbose=True)
    asymmetric.export_public_key(key_name='public_key.pem', verbose=True)

    asymmetric.load_private_key(key_name='private_key.pem', verbose=True)
    asymmetric.load_public_key(key_name='public_key.pem', verbose=True)

    asymmetric.encrypt(file_name='a.txt', verbose=True)
    asymmetric.decrypt(file_name='a.txt', verbose=True)

    # Delete folders
    delete_folder(path=pk_folder, verbose=False)
    delete_folder(path=pbk_folder, verbose=False)
    delete_folder(path=originals, verbose=False)
    delete_folder(path=encrypted, verbose=False)
    delete_folder(path=decrypted, verbose=False)
