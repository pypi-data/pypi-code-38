from random import randint
            
a = ['quiz', 'pynbs']

#App Code:
def quiz():
    n1 = randint(1,10)
    n2 = randint(1,10)
    answer = input('What is '+str(n1)+'x'+str(n2)+'? ')
    if(answer==str(n1*n2)):
        print('Correct!')
        app(a)
    else:
        print('Incorrect!')
        app(a)
def pynbs():
    prnt = input()
    print(prnt)
    app(a)
#App Code End
def app(a):
    openapp = input('What app do you want to open? ')
    if openapp in a:
        method_name = openapp # set by the command line options
        possibles = globals().copy()
        possibles.update(locals())
        method = possibles.get(method_name)
        method()
#Admin Stuff
def wart():
    print('Welcome Admin!')
    an = len(a)
    print('Apps Installed:')
    for i in range(0, an):
        print(' '+a[i])
    app(a)