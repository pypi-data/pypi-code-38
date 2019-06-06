
def play():
  import random
  import time

  print(" ")
  print(" ")

  print("Hello Player, this is a simplified ECON3 version of Battleship.")

  nickname = input("First of all, choose your name : ")

  time.sleep(2)

  print(" ")
  print(" ")

  print("Here are the rules:")

  time.sleep(1)

  print(" ")

  print("Your opponent is the computer, he has put his ship on one field and your goal is to find on which one")
  print("You don't have to put your ship anyway, it is an one way fight")

  time.sleep(5)

  print(" ")

  print("Just imagine that you are not a ship, but a missile, I don't know, who cares?")

  time.sleep(3)

  print(" ")
  print(" ")

  print("Here is an example of ennemy's battlefield:")

  time.sleep(1)

  print("    __1___2___3___4___5__")
  print("   1|___|___|___|___|___|")
  print("   2|___|___|___|___|___|")
  print("   3|___|___|___|___|___|")
  print("   4|___|___|___|___|___|")
  print("   5|___|___|___|___|___|")

  time.sleep(6)

  print("Good Luck!" + str(nickname))

  time.sleep(1)

  target_column = 0
  target_row = 0

  def win(win):
    if boat_column == target_column and boat_row == target_row:
      return 1

  boat_column = random.randint(1,5)
  boat_row = random.randint(1,5)


  while win(win) != 1:
    print("Aim a column and a row")
    target_column = int(input("Which column do you want to target? : "))
    target_row = int(input("Which row do you want to target? : "))
    if win(win):
      print(" ")
      print ("CONGRATS, YOU WON!!!")
      time.sleep(2)
      print(" ")
      print ("YOU ARE A TRUE CHAMPION!!!")
      time.sleep(2)
      print(" ")
      print ("AMERICA NEEDS MEN LIKE YOU!!!")
      time.sleep(3)
      print(" ")
      print("Oh, sorry...mistake...")
      time.sleep(3)
      print(" ")
      print("BELGIUM NEEDS MEN LIKE YOU!!!")
      time.sleep(2)
      print("THANKS FOR PLAYING!!!")
      time.sleep(2)
      print(" ")
      print("   |     |")
      print("   |     |")
      print("   _______")
      print("   \     /")
      print("    \___/")
      print("")
      print("")
      print("")
      time.sleep(2)
      print("OBAMA OUT")
      break
    else:
      print ("TRY AGAIN")
      print("    __1___2___3___4___5__")
      print("   1|___|___|___|___|___|")
      print("   2|___|___|___|___|___|")
      print("   3|___|___|___|___|___|")
      print("   4|___|___|___|___|___|")
      print("   5|___|___|___|___|___|")


