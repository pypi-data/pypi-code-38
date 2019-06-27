from router.map_route.map_route import MapRouter


class GaiaRouter():
    def __init__(self, *args, **kwargs):
        pass

    def run(self):
        """
        Execute the router module.
        """
        # get_area
        points = [(-15.82395, -47.8449737), (-15.822749, -47.8444752)]
        # get base
        base = (-15.82395, -47.8449737)
        current_position = base

        router = MapRouter(points[0], points[1], current_position, base)

        route = router.trace_diagonal_route(
            router.current_position, router.points[0])

        while(True):
            if(len(route) == 1):
                route += router.trace_collection_route(route[0])
                print(route)
            elif(route[0][1] > points[1][1]):
                break
            else:
                # verify if exists obstacles
                go = input("go? ")
                if(go == "y"):
                    # send to GPS
                    router.current_position = route.pop(0)
                elif(go == "c"):
                    break
                else:
                    print("asdkasdhaskjdh")
                    route = router.trace_evasion_route(route)
            print(route)

        route = router.trace_route_to_base()

        while(True):
            if(route == []):
                break
            else:
                # verify if exists obstacles
                go = input("go? ")
                if(go):
                    # send to GPS
                    router.current_position = route.pop(0)
                else:
                    route = trace_evasion_route(route)
            print(route)


if __name__ == "__main__":
    print("===== BEGINNING GAIA BOAT ROUTER")
    router = GaiaRouter()
    router.run()
