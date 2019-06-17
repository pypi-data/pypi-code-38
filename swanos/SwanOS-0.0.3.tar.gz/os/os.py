import os
from User import *
from Admin import *

#A Very Simple Sign In System
users = ['Admin', 'User']
m = 'pass'
d = 'pass'
w = 'pass'
k = 'pass'

def passw():
    passw = input('What is your password? ')
    for i in range(0, 4):
        if name==users[i]:
            if users[i]=='User':
                mart()
            else:
                if users[i]=='Admin':
                    wart()
                
name = input('What is your username? ')
if name in users:
    print()
    passw()
else:
    print('ERROR: User not defined')

