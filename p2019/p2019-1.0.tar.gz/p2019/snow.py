import turtle as t
import  math


def mid(p1, p2):
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)

def skip(x,y):
    t.penup()
    t.goto(x,y)
    t.pendown()

def dis(p1,p2):
    return (((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)**0.5)
#计算角度
def du(x1, y1, x2, y2):

    angle = 0.0
    dx = x2 - x1
    dy = y2 - y1
    if x2 == x1:
        angle = math.pi / 2.0
        if y2 == y1:
            angle = 0.0
        elif y2 < y1:
            angle = 3.0 * math.pi / 2.0
    elif x2 > x1 and y2 > y1:
        angle = math.atan(dy / dx)
    elif x2 > x1 and y2 < y1:
        angle =2* math.pi- math.atan(-dy / dx)
    elif x2 < x1 and y2 < y1:
        angle = math.pi + math.atan(dy / dx)
    elif x2 < x1 and y2 > y1:
        angle = math.pi / 2.0 + math.atan(-dx / dy)
    elif y2 == y1 and x2<x1:
        angle = math.pi
    elif y2 == y1 and x2>x1:
        angle = 0.0
    return (angle * 180 / math.pi)

def f4(p1, p2, n):
    skip(p1[0], p1[1])
    t.goto(p2)
    d=du(p1[0], p1[1], p2[0], p2[1])
    t.seth(d)
    p3=mid(p1 , p2)
    skip(p3[0] , p3[1])
    t.left(60)
    t.fd(dis(p1,p2)/3)
    p4=t.position()
    skip(p3[0],p3[1])
    t.right(120)
    l=dis(p1, p2) / 3
    t.fd(l)
    p5=t.position()
    n-=1
    if n > 0:
        f4(p1, p3, n)
        f4(p3, p2, n)
        f4(p3, p4, n)
        f4(p3, p5, n)
    #skip(0,0)


t.speed(0)
t.ht()
#for p in [(200,0),(100,100*3**0.5),(-100,100*3**0.5),(-200,0),(-100,-100*3**0.5),(100,-100*3**0.5)]:
    #f4((0, 0), p, 2)
for p in [(0,200),(-100*3**0.5,100),(-100*3**0.5,-100),(0,-200),(100*3**0.5,-100),(100*3**0.5,100)]:
    f4((0, 0), p, 2)
t.done()
