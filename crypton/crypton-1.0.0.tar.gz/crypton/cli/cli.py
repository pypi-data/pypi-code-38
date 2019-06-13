from termcolor import colored
from crypton import errors


class Cli:

    def __init__(self):
        self.author = "Overwatch Heir"
        self.version = "1.0.0"
        self.banner = r""" 
            ::::::::  :::::::::  :::   ::: ::::::::: ::::::::::: ::::::::  ::::    ::: 
            :+:    :+: :+:    :+: :+:   :+: :+:    :+:    :+:    :+:    :+: :+:+:   :+: 
            +:+        +:+    +:+  +:+ +:+  +:+    +:+    +:+    +:+    +:+ :+:+:+  +:+ 
            +#+        +#++:++#:    +#++:   +#++:++#+     +#+    +#+    +:+ +#+ +:+ +#+ 
            +#+        +#+    +#+    +#+    +#+           +#+    +#+    +#+ +#+  +#+#+# 
            #+#    #+# #+#    #+#    #+#    #+#           #+#    #+#    #+# #+#   #+#+# 
             ########  ###    ###    ###    ###           ###     ########  ###    #### """ + '\n'

        self.crypton_cli = colored("[CRYPTON]> ", 'blue')
        self.gen_cli = colored("[CRYPTON::GENERATOR]> ", 'blue')
        self.check_cli = colored("[CRYPTON::CHECK]> ", 'blue')
        self.options = [0, 1, 2, 3, 4, 5]

    def display_banner(self):
        print(colored(self.banner, 'blue'))
        print(colored('             * Version: ' + self.version, 'blue'))
        print(colored('             * Created by: ' + self.author, 'blue'))
        print(colored("             * Take a look at README.md file for more info about the program\n", 'blue'))

    def display_menu(self):
        self.display_banner()
        print(colored("\r\n[*] Here you will have to choose between the available options. Select from menu:\n",
                      'green'))
        print(colored("     [1] Secure passwords generation", 'green'))
        print(colored("     [2] Passwords strength & security checks", 'green'))
        print(colored("     [3] Symmetric cryptography", 'green'))
        print(colored("     [4] Asymmetric cryptography", 'green'))
        print(colored("     [5] Hash Algorithms", 'green'))
        print()
        print(colored("     [0] Exit the CryptOn tool", 'green'))
        print()

    def get_option(self, prompt):
        while True:
            try:
                input_option = int(input(prompt))
                print()
                if input_option in self.options:
                    return input_option
                else:
                    print(errors.menu)

            except ValueError:
                print(errors.value_type)
                continue
            except KeyboardInterrupt:
                quit()

    def display_password_generator(self):
        while True:

            try:
                input_length = input(self.gen_cli + colored("Password length (default is 16) : ", 'green'))
                input_n_password = input(self.gen_cli + colored("Number of passwords (default is 1): ", 'green'))

                if not input_length:
                    input_length = 16

                if not input_n_password:
                    input_n_password = 1

                input_length = int(input_length)
                input_n_password = int(input_n_password)

                if input_length < 16 or input_n_password < 1:
                    print(errors.value)
                    continue
                else:
                    return input_length, input_n_password

            except ValueError:
                print(errors.value_type)
                continue
            except KeyboardInterrupt:
                quit()

    def display_password_checker(self):
        while True:
            try:
                input_password = input(self.check_cli + colored("Type your password to check: ", 'green'))

                if not input_password:
                    print(errors.value_empty)
                else:
                    return input_password
            except KeyboardInterrupt:
                quit()
