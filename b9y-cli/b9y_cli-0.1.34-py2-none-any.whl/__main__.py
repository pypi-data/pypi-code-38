#!/usr/bin/env python
#from sys import argv
import sys, getpass
import json, signal, shlex, string
from cmd import Cmd
from b9y import B9y
#from b9y_dev import B9y

b9y_cli_release = "0.1.34"
default_user = "admin"
default_password = "changeme"
default_host="http://localhost:8080"
debug = False

def output(content, type=""):
    try:
        print(str(content))
    except:
        output("ERROR: output contains binary or UTF-8 content that this terminal cannot render.")

def signal_handler(sig, frame):
        output('Bye!')
        sys.exit(0)

def getopts(argv):
    opts = {}
    while argv:
        if argv[0][0] == '-':
            try:
                opts[argv[0]] = argv[1]
            except:
                opts[argv[0]] = ""
        argv = argv[1:]
    return opts

def remove_quotes(param):
    if param.startswith('"') and param.endswith('"'):
        return(param[1:-1])

    if param.startswith("'") and param.endswith("'"):
        return(param[1:-1])

    return(param)

class b9y_prompt(Cmd):
    args = getopts(sys.argv)

    if '-v' in args:
        output("B9y CLI version " + b9y_cli_release)
        sys.exit(0)

    if '-h' in args:
        b9y_host = args['-h']
    else:
        b9y_host = default_host

    if '-u' in args:
        b9y_user = args['-u']
    else:
        b9y_user = default_user

    if '-p' in args:
        b9y_password = args['-p']
        if b9y_password == "":
            b9y_password = getpass.getpass()
    else:
        b9y_password = default_password

    try:
        b9y = B9y(b9y_host, b9y_user, b9y_password)
    except:
        output("""ERROR: unable to connect or credentials not valid.
Try using parameters to specifiy hostname and credentials, e.g.

b9y-cli -h http://localhost:8888
b9y-cli -h http://b9y.myhost.com:8080 -u user1 -p secret
b9y-cli -h http://b9y.myhost.com:8080 -u user1 -p

""")
        sys.exit()

    b9y_instance, b9y_release = b9y.info()

    output("Bambleweeny CLI Version " + b9y_cli_release + "\nConnected to " + b9y_instance + " as " + b9y_user)

    prompt = "b9y v" + str(b9y_release) + "> "
    intro = "Welcome! Type ? to list commands"

    def do_token(self, inp):
        output(self.b9y.get_token())

    def do_save(self, inp):
        r = self.b9y.save()
        if r == None:
            output("error - are you admin?")
        else:
            output("ok")

    def do_exit(self, inp):
        output("Bye!")
        return True

    def do_EOF(self, inp):
        output("Bye!")
        return True

    def help_exit(self):
        output('Exit the application.')

    def do_create_user(self, inp):
        items = shlex.split(inp, posix=False)
        if len(items) != 2:
            output("Error: need exactly two arguments.")
            return(None)
        try:
            r = self.b9y.create_user(items[0], items[1])
            output("OK. New user id is " + str(r))
        except:
            output("error")

    def do_password(self, inp):
        items = shlex.split(inp, posix=False)
        if len(items) != 1:
            output("Error: need exactly two arguments.")
            return(None)
        try:
            r = self.b9y.set_admin_password(items[0])
            output("OK. Please login again with the new password.")
            self.b9y.token = "PLEASELOGINAGAIN"
        except:
            output("error")

    def do_users(self, inp):
        try:
            r = self.b9y.list_users()

            for k in r["users"]:
                output("USER: " + k['username'] + " ID: " + str(k['id']) + " QUOTA: " + str(k['quota']))
        except:
            output("Error. Are you admin?")

    def do_set(self, inp):
        items = shlex.split(inp, posix=False)
        if len(items) != 2:
            output("Error: need exactly two arguments.")
            return(None)
        r = self.b9y.set(items[0], remove_quotes(items[1]))
        if r:
            output("OK")

    def do_del(self, inp):
        items = shlex.split(inp, posix=False)
        if len(items) != 1:
            output("Error: need exactly one argument.")
            return(None)
        try:
            r = self.b9y.delete(items[0])
            if r:
                output("OK")
        except:
            output("Error")

    def do_route(self, inp):
        items = shlex.split(inp, posix=False)
        if len(items) != 2:
            output("Error: need exactly two arguments.")
            return(None)
        r = self.b9y.create_route(items[0], remove_quotes(items[1]))
        if r:
            output(r)

    def do_bin(self, inp):
        items = shlex.split(inp, posix=False)
        if len(items) != 1:
            output("Error: need exactly one argument.")
            return(None)
        r = self.b9y.create_bin(items[0])
        if r:
            output(r)

    def do_push(self, inp):
        items = shlex.split(inp, posix=False)
        if len(items) != 2:
            output("Error: need exactly two arguments.")
            return(None)
        r = self.b9y.push(items[0], remove_quotes(items[1]))
        if r:
            output("OK")

    def do_incr(self, inp):
        items = shlex.split(inp, posix=False)
        if len(items) != 1:
            output("Error: need exactly one argument.")
            return(None)
        r = self.b9y.incr(items[0])
        if r != None:
            output(str(r))
        else:
            output("Error")

    def do_get(self, inp):
        items = shlex.split(inp, posix=False)
        if len(items) != 1:
            output("Error: need exactly one argument.")
            return(None)
        r = self.b9y.get(items[0])
        output(r)

    def do_keys(self, inp):
        items = shlex.split(inp, posix=False)
        if len(items) == 0:
            r = self.b9y.keys()
        else:
            try:
                r = self.b9y.keys(items[0])
            except:
                return(None)
        for k in r:
            output(k)

    def do_pop(self, inp):
        items = shlex.split(inp, posix=False)
        if len(items) != 1:
            output("Error: need exactly one argument.")
            return(None)
        r = self.b9y.pop(items[0])
        output(str(r))

    def help_set(self):
        output("Set a Key. Example: set foo bar")

    def help_del(self):
        output("Delete a Key. Example: del foo")

    def help_create_user(self):
        output("** for admin use** Create a User. Example: create_user user1 secret")

    def help_password(self):
        output("** for admin use** Set the admin password. Example: password secret")

    def help_users(self):
        output("** for admin use** Lists all users")

    def help_save(self):
        output("** trigger a 'save' on Redis to dump data to the filesystem")

    def help_token(self):
        output("Gives you a bearer token for including in HTTP requests")

    def help_route(self):
        output("Make key publicly readable. Example: route foo text/html")

    def help_bin(self):
        output("Create a public POST bin for a list. Example: bin my_list")

    def help_keys(self):
        output("List all Keys. You may specifiy an oprtional search string, 'grep style'.\nExample: keys\nExample: keys sys")

    def help_get(self):
        output("Get a Key. Example: get foo")

    def help_push(self):
        output("Adds a value to a list / queue. Example: push foo bar")

    def help_pop(self):
        output("Retrieves an item from a list. Example: pop foo")

    def help_incr(self):
        output("Increase Counter. Example: incr ticket_number")

    def emptyline(self):
        dummy = 1

    def default(self, inp):
        if inp == 'q':
            return self.do_exit(inp)

        output("No idea what you want! Type 'help' for available commands.")

def main():
    signal.signal(signal.SIGINT, signal_handler)
    b9y_prompt().cmdloop()

if __name__ == '__main__':
    main()
