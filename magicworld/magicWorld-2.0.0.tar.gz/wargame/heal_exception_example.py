from wargame.knight import Knight
from wargame.gameuniterror import GameUnitError
import logging
if __name__ == '__main__':
    print("Creating a Knight..")
    knight = Knight("Sir Bar")
    knight.health_meter = 10
    knight.show_health()
    try:
        knight.heal(heal_by=100, full_healing=False)
    except GameUnitError as e:
        print(e)
        logging.info(e.error_message)
    knight.show_health()