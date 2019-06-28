import math
from router.map_route.map_route import MapRouter as Router


class GaiaControl():

    def __init__(self):
        # TODO recive area from app
        # points = [(-15.82395, -47.8449737),(-15.822749,-47.8444752)]
        points = [(0, 0), (5, 5)]
        # TODO recive base location from app
        # base = (-15.82395, -47.8449737)
        base = (0, 0)
        # TODO recive current position from gps
        current_position = base

        # TODO recive direction
        self.direction = 0

        self.router = Router(points[0], points[1], current_position, base)
        # TODO init object detection
        self.route = self.router.trace_diagonal_route(
            self.router.current_position, self.router.points[0])
        self.state = 'collecting'
        self.was_collecting = False
        self.was_returning = False

    def run(self):
        while(self.state != 'final'):
            print(self.state)
            if(self.state == 'collecting'):
                self.collecting()
            elif(self.state == 'evading'):
                self.evading()
            elif(self.state == 'returning_to_base'):
                self.returning_to_base()
            elif(self.state == 'waiting'):
                self.waiting()
            else:
                self.state = 'final'

    # This method is responsible to control the boat actions when in route
    def in_route(self):
        while(len(self.route) > 0):
            print(self.route)
            # verifies if the next point in the route is out of the
            # collection area
            if(self.route[0][1] > self.router.points[1][1]):
                self.state = 'returning_to_base'
                self.route = self.router.trace_route_to_base()
                break

            else:
                # TODO verify boat status
                # TODO verify if exists obstacles
                go = input("go? ")

                new_direction = self.direction_change_angle()
                direction_diference = new_direction - self.direction
                print(self.direction, new_direction, direction_diference)
                if(direction_diference != 0):
                    if(direction_diference > 0):
                        direction_diference += (2*math.pi)
                    # send the angle to eletronic
                    # wait for the response
                    self.direction = new_direction
                    print('changed')

                if(go == "y"):
                    # TODO send to point GPS
                    # TODO wait response
                    self.router.current_position = self.route.pop(0)
                # goes to base if the status verification is "bad"
                elif(go == "c"):
                    if(self.state == "collecting"):
                        self.was_collecting = True
                        self.collection_route = self.route
                    self.state = 'returning_to_base'
                    self.route = self.router.trace_route_to_base()
                    break
                # evades if a obstacle was found
                else:
                    print("asdkasdhaskjdh")
                    if(self.state == "returning_to_base"):
                        self.was_returning = True
                        self.return_route = self.route
                        self.return_route.pop(0)
                    elif(self.state == "collecting"):
                        self.was_collecting = True
                        self.collection_route = self.route
                        self.collection_route.pop(0)
                    elif(self.state == "evading"):
                        aux += self.router.trace_evasion_route(self.route)
                        self.route.pop(0)
                        self.route = aux + self.route
                        break
                    self.state = 'evading'
                    self.route = self.router.trace_evasion_route(self.route)
                    break

    # method responsible to control the boat when in the default collection
    # route
    def collecting(self):
        if(self.route == []):
            self.route = self.router.trace_collection_route(
                self.router.current_position)
        self.in_route()

    # method responsible to control the boat when in tracing a evasion route
    def evading(self):
        if(self.route == []):
            if(self.was_returning):
                self.state = "returning_to_base"
                self.route = self.return_route
                self.was_returning = False
                self.return_route = []
            elif(self.was_collecting):
                self.state = "collecting"
                self.route = self.router.trace_diagonal_route(
                    self.router.current_position, self.collection_route[0])
                self.route += self.collection_route
                self. was_collecting = False
                self.collection_route = []
            return
        self.in_route()

    # method responsible to control the boat when going to base
    def returning_to_base(self):
        if(self.route == []):
            self.state = "waiting"
            return
        print("aqui")
        print(self.route)
        self.in_route()

    # method responsible to control the boat when in waiting
    def waiting(self):
        # wait signal

        signal = input("signal? ")
        if(self.was_collecting):
            self.state = "collecting"
            self.route = self.router.trace_diagonal_route(
                self.router.current_position, self.collection_route[0])
            self.route += self.collection_route
            self. was_collecting = False
            self.collection_route = []
        else:
            self.state = "final"

    def direction_change_angle(self):

        x0 = self.router.current_position[0]
        y0 = self.router.current_position[1]
        x1 = self.route[0][0]
        y1 = self.route[0][1]

        dist_x = x1 - x0
        dist_y = y1 - y0

        if(dist_x == 0 and dist_y == 0):
            return self.direction

        print("x - ", dist_x)
        print("y - ", dist_y)

        if(dist_x == 0):
            if(dist_y > 0):
                return math.pi/2
            else:
                return 3*math.pi/2

        if(dist_y == 0):
            if(dist_x > 0):
                return 0
            else:
                return math.pi

        tg = abs(dist_y/dist_x)
        angle = math.atan(tg)
        if(dist_x > 0):
            if(dist_y > 0):
                return angle
            else:
                return angle + (3*math.pi/4)
        else:
            if(dist_y > 0):
                return angle + math.pi/2
            else:
                return angle + math.pi/4

        return angle
