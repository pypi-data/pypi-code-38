from msgtools.lib.messaging import Messaging as M
from msgtools.lib.message import Message as Msg
from msgtools.console.client import Client

def my_fn():
    # do stuff
    for i in range(0,10):
        print(i)

my_fn()

M.LoadAllMessages()
cxn = Client('example')

tc2 = M.Messages.TestCase2()
print('tc2: ' + tc2.toJson())
tc2 = Msg.fromJson({"TestCase2": {"F1": "Val1", "F2": ["1.0", "2.0", "4.0"], "F3": "13.0", "F4": "50.0", "Field5": "0", "Field6": 1}})
print('tc2: ' + tc2.toJson())

tc1 = M.Messages.TestCase1(FieldC=[3,2,1], FieldA=2, FieldE=2.71828, FieldF=28.828)
tc1.FieldB = 3
print('fb : ' + str(tc1.FieldA))
print('fc : ' + str(tc1.FieldC))
print('fc[2] : ' + str(tc1.FieldC[2]))
print('sending ' + tc1.toJson())
for i in range(0,5):
    tc1.FieldA = i
    cxn.send(tc1)
msg = cxn.recv(M.Messages.TestCase2, timeout=3)
if not msg:
    print("didn't get tc2")
else:
    print('F1 is ' + str(msg.F1))
    print(msg.toJson())

for i in range(0,5):
    msg = cxn.recv(timeout=10)
    print(msg.toJson())