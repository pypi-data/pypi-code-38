import base64

from termcolor import colored

from crypton.cli.cli_asymmetric import CliAsymmetric
from crypton.cli.cli_dsa import CliDSA
from crypton.cli.cli_ecdsa import CliECDSA
from crypton.cli.cli_ed25519 import CliED25519
from crypton.cli.cli_hash import CliHash
from crypton.cli.cli_rsa import CliRSA
from crypton.cli.cli_symmetric import CliSymmetric
from crypton.cli.cli_x25519 import CliX25519
from crypton.cli.cli_x509 import CliX509
from crypton.crypt_algorithms.asymmetric.X509 import X509
from crypton.crypt_algorithms.asymmetric.dsa import DSA
from crypton.crypt_algorithms.asymmetric.ecdsa import ECDSA
from crypton.crypt_algorithms.asymmetric.ed25519 import ED25519
from crypton.crypt_algorithms.asymmetric.rsa import RSA
from crypton.crypt_algorithms.asymmetric.x25519 import X25519
from crypton.crypt_algorithms.hash.sha2 import SHA2
from crypton.crypt_algorithms.hash.sha3 import SHA3
from crypton.crypt_algorithms.symmetric.aes import Aes


def symmetric():
    cli = CliSymmetric()
    cli.display_menu()
    option = cli.get_option(prompt=cli.aes_cli)

    while option != 0:
        if option == 1:
            key_size, passphrase = cli.display_key_generator()
            key = Aes(key_size=key_size, passphrase=passphrase).generate_key()
            key = base64.b64encode(key).decode('utf-8')
            print(colored('\n    Key : ', 'green') + key + '\n')

        if option == 2:
            key, mode, text_file_path = cli.display_encrypt()
            Aes().encrypt_file(key=key, mode=mode, text_file_path=text_file_path)
            print(colored('\n  File successfully encrypted! \n ', 'green'))

        if option == 3:
            key, mode, text_file_path = cli.display_decrypt()
            Aes().decrypt_file(key=key, mode=mode, text_file_path=text_file_path)
            print(colored('\n  File successfully decrypted! \n ', 'green'))

        option = cli.get_option(prompt=cli.aes_cli)


def asymmetric():
    cli = CliAsymmetric()
    cli.display_menu()
    option = cli.get_option(prompt=cli.asymm_cli)

    while option != 0:
        if option == 1:
            _asymmetric_rsa()

        if option == 2:
            _asymmetric_dsa()

        if option == 3:
            _asymmetric_ecdsa()

        if option == 4:
            _asymmetric_ed25519()

        if option == 5:
            _asymmetric_x25519()

        if option == 6:
            _asymmetric_x509()

        option = cli.get_option(prompt=cli.asymm_cli)


def _asymmetric_rsa():
    cli = CliRSA()
    cli.display_menu()
    option = cli.get_option(prompt=cli.rsa_cli)

    while option != 0:
        if option == 1:
            key_size, key_file_path = cli.display_key_generator(key='RSA')

            if len(key_file_path) == 0:
                RSA(key_size=key_size).file_key_pair()
            else:
                RSA(key_size=key_size).file_key_pair(file_path=key_file_path)

            print(colored('\n  RSA key pair generated! \n ', 'green'))

        if option == 2:
            key_size, key_file_path = cli.display_key_generator(key='RSA')

            if len(key_file_path) == 0:
                RSA(key_size=key_size).file_key_pair(ssh=True)
            else:
                RSA(key_size=key_size).file_key_pair(ssh=True, file_path=key_file_path)

            print(colored('\n  RSA key pair for SSH Auth generated! \n ', 'green'))

        if option == 3:
            text_file_path, private_key_path = cli.display_sign(key='RSA')
            RSA().file_sign(text_file_path=text_file_path, private_key_path=private_key_path)

            print(colored('\n  File successfully signed using RSA ! \n ', 'green'))

        if option == 4:
            text_file_path, public_key_path, signature_path = cli.display_verify(key='RSA')
            verified = RSA().verify(text_file_path=text_file_path,
                                    public_key_path=public_key_path,
                                    signature_path=signature_path)
            if verified:
                print(colored('\n  Signature verified using RSA ! \n ', 'green'))
            else:
                print(colored('\n  Invalid signature! \n ', 'green'))

        if option == 5:
            text_file_path, public_key_path = cli.display_encrypt(key='RSA')
            RSA().file_encrypt(text_file_path=text_file_path, public_key_path=public_key_path)

            print(colored('\n  File successfully encrypted using RSA ! \n ', 'green'))

        if option == 6:
            encrypted_file_path, private_key_path, aes_key_path = cli.display_decrypt()
            RSA().file_decrypt(aes_key_path=aes_key_path,
                               private_key_path=private_key_path,
                               encrypted_file_path=encrypted_file_path)

            print(colored('\n  File successfully decrypted using RSA ! \n ', 'green'))

        option = cli.get_option(prompt=cli.rsa_cli)


def _asymmetric_dsa():
    cli = CliDSA()
    cli.display_menu()
    option = cli.get_option(prompt=cli.dsa_cli)

    while option != 0:
        if option == 1:
            key_size, key_file_path = cli.display_key_generator(key='DSA')
            if len(key_file_path) == 0:
                DSA(key_size=key_size).file_key_pair()
            else:
                DSA(key_size=key_size).file_key_pair(file_path=key_file_path)

            print(colored('\n  DSA key pair generated! \n ', 'green'))

        if option == 2:
            text_file_path, private_key_path = cli.display_sign(key='DSA')
            DSA().file_sign(text_file_path=text_file_path, private_key_path=private_key_path)

            print(colored('\n  File successfully signed using DSA ! \n ', 'green'))

        if option == 3:
            text_file_path, public_key_path, signature_path = cli.display_verify(key='DSA')
            verified = DSA().verify(text_file_path=text_file_path,
                                    public_key_path=public_key_path,
                                    signature_path=signature_path)
            if verified:
                print(colored('\n  Signature verified using DSA ! \n ', 'green'))
            else:
                print(colored('\n  Invalid signature! \n ', 'green'))

        option = cli.get_option(prompt=cli.dsa_cli)


def _asymmetric_ecdsa():
    cli = CliECDSA()
    cli.display_menu()
    option = cli.get_option(prompt=cli.ecdsa_cli)

    while option != 0:
        if option == 1:
            key_size, key_file_path = cli.display_key_generator(key='ECDSA')

            if len(key_file_path) == 0:
                ECDSA(key_size=key_size).file_key_pair()
            else:
                ECDSA(key_size=key_size).file_key_pair(file_path=key_file_path)

            print(colored('\n  ECDSA key pair generated! \n ', 'green'))

        if option == 2:
            text_file_path, private_key_path = cli.display_sign(key='ECDSA')
            ECDSA().file_sign(text_file_path=text_file_path, private_key_path=private_key_path)

            print(colored('\n  File successfully signed using ECDSA ! \n ', 'green'))

        if option == 3:
            text_file_path, public_key_path, signature_path = cli.display_verify(key='ECDSA')
            verified = ECDSA().verify(text_file_path=text_file_path,
                                      public_key_path=public_key_path,
                                      signature_path=signature_path)
            if verified:
                print(colored('\n  Signature verified using ECDSA ! \n ', 'green'))
            else:
                print(colored('\n  Invalid signature! \n ', 'green'))

        option = cli.get_option(prompt=cli.ecdsa_cli)


def _asymmetric_ed25519():
    cli = CliED25519()
    cli.display_menu()
    option = cli.get_option(prompt=cli.ed25519_cli)

    while option != 0:
        if option == 1:
            key_file_path = cli.display_key_generator(key='ED25519')

            if len(key_file_path) == 0:
                ED25519().file_key_pair()
            else:
                ED25519().file_key_pair(file_path=key_file_path)

            print(colored('\n  ED25519 key pair generated! \n ', 'green'))

        if option == 2:
            text_file_path, private_key_path = cli.display_sign(key='ED25519')
            ED25519().file_sign(text_file_path=text_file_path, private_key_path=private_key_path)

            print(colored('\n  File successfully signed using ED25519 ! \n ', 'green'))

        if option == 3:
            text_file_path, public_key_path, signature_path = cli.display_verify(key='ED25519')
            verified = ED25519().verify(text_file_path=text_file_path,
                                        public_key_path=public_key_path,
                                        signature_path=signature_path)
            if verified:
                print(colored('\n  Signature verified using ED25519 ! \n ', 'green'))
            else:
                print(colored('\n  Invalid signature! \n ', 'green'))

        option = cli.get_option(prompt=cli.ed25519_cli)


def _asymmetric_x25519():
    cli = CliX25519()
    cli.display_menu()
    option = cli.get_option(prompt=cli.x25519_cli)

    while option != 0:
        if option == 1:
            key_file_path = cli.display_key_generator(key='X25519')

            if len(key_file_path) == 0:
                X25519().file_key_pair()
            else:
                X25519().file_key_pair(file_path=key_file_path)

            print(colored('\n  X25519 key pair generated! \n ', 'green'))

        option = cli.get_option(prompt=cli.x25519_cli)


def _asymmetric_x509():
    cli = CliX509()
    cli.display_menu()
    option = cli.get_option(prompt=cli.x509_cli)

    while option != 0:
        if option == 1:
            key_size, algorithm, subject, alternative, email, org, org_unit, cert_path = cli.display_ss_certificate()

            if len(cert_path) == 0:
                X509(key_size=key_size).file_x509(cert_type='ss',
                                                  algorithm=algorithm,
                                                  subject_name=subject,
                                                  alternative=alternative,
                                                  email=email,
                                                  org=org,
                                                  org_unit=org_unit)

            else:
                X509(key_size=key_size).file_x509(cert_type='ss',
                                                  algorithm=algorithm,
                                                  subject_name=subject,
                                                  alternative=alternative,
                                                  email=email,
                                                  org=org,
                                                  org_unit=org_unit,
                                                  file_path=cert_path)

            print(colored('\n  Self signed certificate and key successfully created! \n ', 'green'))

        if option == 2:
            key_size, algorithm, subject, alternative, email, org, org_unit, cert_file_path = cli.display_csr()
            domains = alternative.split(', ')

            if len(cert_file_path) == 0:
                X509(key_size=key_size).file_x509(cert_type='csr',
                                                  algorithm=algorithm,
                                                  subject_name=subject,
                                                  alternative=domains,
                                                  email=email,
                                                  org=org,
                                                  org_unit=org_unit)

            else:

                X509(key_size=key_size).file_x509(cert_type='csr',
                                                  algorithm=algorithm,
                                                  subject_name=subject,
                                                  alternative=domains,
                                                  email=email,
                                                  org=org,
                                                  org_unit=org_unit,
                                                  file_path=cert_file_path)

            print(colored('\n  CSR and key successfully created! \n ', 'green'))

        option = cli.get_option(prompt=cli.x509_cli)


def hashing():
    cli = CliHash()
    cli.display_menu()
    option = cli.get_option(prompt=cli.hash)

    while option != 0:
        file_path, sha_size = cli.display_hash(hash_option=option)

        if option == 1:
            SHA3(bits=sha_size).file_digest(file_path=file_path)
            print(colored('\n  Text successfully hashed using SHA3! \n ', 'green'))

        if option == 2:
            SHA2(bits=sha_size).file_digest(file_path=file_path)
            print(colored('\n  Text successfully hashed using SHA2! \n ', 'green'))

        option = cli.get_option(prompt=cli.hash)
