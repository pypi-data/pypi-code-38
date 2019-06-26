import pygame
import random
import time
from pygame.time import get_ticks

##################################
#
#
#
#  OBS: My first ever program, therefore HORRIBLE coding.
#
#
#
#
#

pygame.init()
pygame.mixer.music.load('resources/music.wav')
diesound = pygame.mixer.Sound('resources/diesound.wav')
pygame.mixer.Sound.set_volume(diesound, 0.05)
duck = False
coinsound = pygame.mixer.Sound('resources\\coinsound.wav')

dead_duck = False
grass = pygame.image.load('resources\\grass.png')
duck = pygame.image.load('resources\\duck.png')
coin_image = pygame.image.load('resources\\coin.png')
font = pygame.font.SysFont(None, 30)

last_pressed = ''
before_pressed = ''
duck_list = []
laser = False
duck_x = 0
duck_y = 0
running = False
transformed_duck = pygame.transform.rotate((pygame.image.load('resources\\duck.png')), 180)
fall = 0
where_big_block = 0
amount = 0
universal_width = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
universal_water = []
already = False

fall1 = 0
running1 = False
amount1 = 0
where_coin1 = 0
lily = pygame.image.load('resources\\lily.png')
picture = lily
clock = pygame.time.Clock()
width = 800
length = 600
displayGame = pygame.display.set_mode((width, length))
pygame.display.set_caption('Lillypod Dodge ULTIMATE VErSIOn')

green = (0, 155, 0)
blue = (0, 0, 155)
yellow = (255, 255, 0)
red = (255, 0, 0)

block_size = 15
big_block_size = 40


def right_pressed(before_pressed):
    return 'right', True, before_pressed


def left_pressed(before_pressed):
    return 'left', True, before_pressed


def down_pressed(before_pressed):
    return 'down', True, before_pressed


def up_pressed(before_pressed):
    return 'up', True, before_pressed


def right_release(before_pressed):
    return before_pressed, False


def left_release(before_pressed):
    return before_pressed, False


def down_release(before_pressed):
    return before_pressed, False


def up_release(before_pressed):
    return before_pressed, False

class MakeLilly:

    def __init__(self, x):
        global fall, amount, universal_width, running, where_big_block, picture, transformed_duck, duck_x, duck_y, duck_list, dead_duck
        self.picture = picture
        self.fall = fall
        self.dead_duck = dead_duck
        self.amount = amount
        self.running = running
        self.transformed_duck = transformed_duck
        self.where_big_block = where_big_block
        self.duck_x = duck_x
        self.duck_y = duck_y
        lily1 = True
        self.lily1 = lily1
        self.duck_list = duck_list
        #self.place_lilly(x)

    def place_lilly(self, x, speed, lowspeed, where_duck):
        global universal_width
        if self.amount == 0:
            self.amount = random.randrange(lowspeed, speed - 1)
            kol = random.randrange(1, 10)
            if kol == 1:
                self.lily1 = False
            if self.lily1 == True:
                self.picture = lily
            elif self.lily1 == False:
                self.picture = self.transformed_duck
            self.dead_duck = False
        self.fall += self.amount
        if self.fall > (length + 40):
            self.running = False
            self.fall = 0
            self.amount = 0
            self.where_big_block = random.randrange(big_block_size, width - big_block_size, big_block_size)
            while self.where_big_block in universal_width:
                self.where_big_block = random.randrange(big_block_size, width - big_block_size, big_block_size)

        if self.running == False:
            self.where_big_block = random.randrange(big_block_size, width - big_block_size, big_block_size)
            while self.where_big_block in universal_width:
                self.where_big_block = random.randrange(big_block_size, width - big_block_size, big_block_size)
        universal_width[x] = self.where_big_block
        self.duck_list = []
        self.duck_list = [self.where_big_block,  -big_block_size + self.fall]
        rekna = -1
        treff = -1
        if self.lily1 == False and self.dead_duck == False:
            rekna = -1
            for temp in where_duck:
                if self.dead_duck == False:
                    rekna = rekna + 1
                    x_list = []
                    y_list = []
                    x_list1 = []
                    y_list1 = []
                    for i in range(7, 30):
                        x_list.append(self.duck_list[0] + i)
                    for l in range(12, 16):
                        y_list.append(self.duck_list[1] + l)

                    for m in range(1, 4):
                        x_list1.append(int(temp[0] + m))
                    for n in range(1, 7):
                        y_list1.append(int(temp[1] + n))

                    for q in x_list:
                        if self.dead_duck == False:
                            for h in y_list:

                                if (q in x_list1) and (h in y_list1):
                                    self.dead_duck = True
                                    treff = rekna
                                    break
        if treff != -1:
            print(treff)
        if self.dead_duck == False or (self.lily1 == True):
            displayGame.blit(self.picture, (self.where_big_block, -big_block_size + self.fall))
        self.running = True
        if (self.dead_duck == False) or (self.lily1 == True):
            return self.where_big_block, -big_block_size + self.fall, self.amount, -1
        else:
            return 0, 0, 100, treff
lilly1 = MakeLilly(1)
lilly2 = MakeLilly(2)
lilly3 = MakeLilly(3)
lilly4 = MakeLilly(4)
lilly5 = MakeLilly(5)
lilly6 = MakeLilly(6)
lilly7 = MakeLilly(7)
lilly8 = MakeLilly(8)
lilly5 = MakeLilly(9)
lilly6 = MakeLilly(10)
lilly7 = MakeLilly(11)
lilly8 = MakeLilly(12)

def show_message(msg, color, y=0, x=0):
    text = font.render(msg, True, color)
    text_rect = text.get_rect(center=(width / 2 + x, length / 2 - y))
    displayGame.blit(text, text_rect)

def coin(lead_x, lead_y):
    is_taken = False
    global universal_width, fall1, running1, amount1, where_coin1, big_block_size, width, length
    fall1 += 1
    b = False

    score = 0

    if fall1 > (length + 40):
        running1 = False
        fall1 = 0
        amount1 = 0
        where_coin1 = random.randrange(big_block_size, width - big_block_size, big_block_size)
        while where_coin1 in universal_width:
            where_coin1 = random.randrange(big_block_size, width - big_block_size, big_block_size)

    if running1 == False:
        where_coin1 = random.randrange(big_block_size, width - big_block_size, big_block_size)
        while where_coin1 in universal_width:
            where_coin1 = random.randrange(big_block_size, width - big_block_size, big_block_size)
    universal_width[13] = where_coin1
    displayGame.blit(coin_image, (where_coin1, fall1 - 40))
    running1 = True

    for x in [int(lead_x), int(lead_x) + 15]:
        if b == True:
            break
        if x > where_coin1 - 7 and x < where_coin1 + 32:
            if b == True:
                break

            for y in [int(lead_y), int(lead_y) + 15]:
                if b == True:
                    break
                if y > fall1 - 45 and y < fall1 - 7:

                    #    if y == y2:
                    score = 50
                    b = True
                    pygame.mixer.Sound.play(coinsound)
                    break
    if b == True:
        fall1 = 0
        where_coin1 = 0
        running1 = False

    return b, score


def score_summon(score, where_duck, lead_x, lead_y, extrascore):


    lowsp = 2
    sp = 4
    coin_taken = False
    fullList = []
    XnY = []


    # When lilys increase depending on score and takes position
    if score < 200:
        sp = 5
    if score > 600:
        sp = 6
    if score > 800:
        lowsp = 3
    if score > 1200:
        sp = 7
    if score > 1500:
        lowsp = 4
    if score > 2000:
        sp = 8
    number = random.randrange(1, 50)
    plus_score = 0
    if number == 9 or coin_taken == False:
        coin_taken, plus_score = coin(lead_x, lead_y)
        extrascore = extrascore + plus_score
    hit = -1
    hitting = []
    if score > 10:
        x, y, z, hit = lilly1.place_lilly(1, sp, lowsp, where_duck)
        XnY = [x, y, z]
        hitting.append(hit)
        fullList.append(XnY)
        if score > 20:
            x, y, z, hit = lilly2.place_lilly(2, sp, lowsp, where_duck)
            hitting.append(hit)
            XnY = [x, y, z]
            fullList.append(XnY)
        if score > 50:
            x, y, z, hit = lilly3.place_lilly(3, sp, lowsp, where_duck)
            hitting.append(hit)
            XnY = [x, y, z]
            fullList.append(XnY)
        if score > 120:
            x, y, z, hit = lilly4.place_lilly(4, sp, lowsp, where_duck)
            hitting.append(hit)
            XnY = [x, y, z]
            fullList.append(XnY)
        if score > 220:
            x, y, z, hit = lilly5.place_lilly(5, sp, lowsp, where_duck)
            hitting.append(hit)
            XnY = [x, y, z]
            fullList.append(XnY)
        if score > 300:
            x, y, z, hit = lilly6.place_lilly(6, sp, lowsp, where_duck)
            hitting.append(hit)
            XnY = [x, y, z]
            fullList.append(XnY)
        if score > 450:
            x, y, z, hit = lilly7.place_lilly(7, sp, lowsp, where_duck)
            hitting.append(hit)
            XnY = [x, y, z]
            fullList.append(XnY)
        if score > 600:
            x, y, z, hit = lilly8.place_lilly(8, sp, lowsp, where_duck)
            hitting.append(hit)
            XnY = [x, y, z]
            fullList.append(XnY)
        if score > 800:
            x, y, z, hit = lilly7.place_lilly(9, sp, lowsp, where_duck)
            hitting.append(hit)
            XnY = [x, y, z]
            fullList.append(XnY)
    return XnY, hitting, fullList, extrascore


def efterflyt(x, y, change, op):

    if change[1] == 0:
        change1 = change[0] / op
        int(change1)
        x = x + change1

    if change[1] == 1:
        change1 = change[0] / op
        y = y + change1
    return x, y

def dots_under_duck(lead_x, lead_y):
    light_blue = (0, 0, 255)
    for i in range(-10, block_size + 10, 3):
        for j in range(10, block_size + 20, 3):
            randnr = random.randrange(1, 800)
            if randnr == 1:
                universal_water.append([i + lead_x, j + lead_y, 0])
    for m in range(0, len(universal_water) - 1):
        universal_water[m][2] = universal_water[m][2] + 1
        universal_water[m][1] = universal_water[m][1] + 1
    for m in range(0, len(universal_water) - 1):
        if universal_water[m][2] == 100:
            universal_water.remove(universal_water[m])
            break
    for l in range(len(universal_water) - 1):
        k = universal_water[l][0]
        s = universal_water[l][1]
        pygame.draw.circle(displayGame, light_blue, [int(k), int(s)], 3)
    for p in range(len(universal_water) - 1):
        if p <= (len(universal_water) - 1):
            if universal_water[p][2] == 50:
                universal_water.remove(universal_water[p])
                break

def gameLoop():
    time_score = 0
    die2 = False
    score = 0
    universal_water1 = []
    last_pressed = ''
    lead_x = width / 2
    lead_y = length / 1.4
    laser = False
    flyt = [0, 0]
    laser_shoot = []
    lead_x_change = 0
    lead_y_change = 1
    on = True
    op = 1
    before_pressed = ''
    death_by_lilly_nr = 3

    extrascore = 0
    is_right_pressed = False
    hitting = []
    is_left_pressed = False
    is_down_pressed = False
    is_up_pressed = False

    die = False
    while on:
        if die == False:
            time_score += 0.1
            score = round(time_score) + extrascore
            for event in pygame.event.get():
                laser = False
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN and die == False:

                    if event.key == pygame.K_d:
                        last_pressed, is_right_pressed, before_pressed = right_pressed(last_pressed)

                    elif event.key == pygame.K_a:
                        last_pressed, is_left_pressed, before_pressed = left_pressed(last_pressed)

                    elif event.key == pygame.K_w:
                        last_pressed, is_up_pressed, before_pressed = up_pressed(last_pressed)
                    elif event.key == pygame.K_SPACE:
                        laser = True

                if event.type == pygame.KEYUP and die == False:
                    if event.key == pygame.K_d:
                        last_pressed, is_right_pressed = right_release(before_pressed)

                    elif event.key == pygame.K_a:
                        last_pressed, is_left_pressed = left_release(before_pressed)

                    elif event.key == pygame.K_w:
                        last_pressed, is_up_pressed = up_release(before_pressed)

                if (last_pressed == 'right') and (is_right_pressed == True):
                    lead_x_change = 4
                    flyt = [lead_x_change, 0]
                    if not (is_down_pressed or is_up_pressed):
                        lead_y_change = 1
                elif (last_pressed == 'left') and (is_left_pressed == True):
                    lead_x_change = -4
                    flyt = [lead_x_change, 0]
                    if not (is_down_pressed or is_up_pressed):
                        lead_y_change = 1
                elif (last_pressed == 'down') and (is_down_pressed == True):
                    lead_y_change = 4
                    flyt = [lead_y_change, 1]
                    if not (is_left_pressed or is_right_pressed):
                        lead_x_change = 0
                elif (last_pressed == 'up') and (is_up_pressed == True):
                    lead_y_change = -3
                    flyt = [lead_y_change, 1]
                    if not (is_left_pressed or is_right_pressed):
                        lead_x_change = 0

                if not (is_right_pressed or is_left_pressed or is_down_pressed or is_up_pressed):
                    op = 4
                    lead_x_change = 0
                    lead_y_change = 2


        else:
            if die2 == True:
                lead_y_change = 2
            else:
                lead_y_change = death_by_lilly_nr

        displayGame.fill(blue)

        # Efterflyt
        if not (is_right_pressed or is_left_pressed or is_down_pressed or is_up_pressed):
            lead_x, lead_y = efterflyt(lead_x, lead_y, flyt, op)

        # Dots under DUCK
        dots_under_duck(lead_x, lead_y)

        # Lightblue water strips
        light_blue = (0, 0, 255)
        for h in range(0, width, 3):
            randnr = random.randrange(1, 7000)
            if randnr == 1:
                universal_water1.append([h, -100])
        for m in range(0, len(universal_water1) - 1):
            universal_water1[m][1] = universal_water1[m][1] + 1
        for l in range(len(universal_water1) - 1):
            k = universal_water1[l][0]
            s = universal_water1[l][1]
            pygame.draw.rect(displayGame, light_blue, [k, s, 3, 100])
        for m in range(0, len(universal_water1) - 1):
            if universal_water1[m][1] >= length:
                universal_water1.remove(universal_water1[m])
                break


        # Prints Duck
        lead_x += lead_x_change
        lead_y += lead_y_change
        displayGame.blit(duck, (lead_x, lead_y))


        #Checks if dead
        if big_block_size-3 >= lead_x or lead_x >= width - big_block_size - 20:
            die = True
            die2 = True
            lead_x_change = 0
        if lead_y > 620 or lead_y < -30:
            if die2 == True:
                pygame.mixer.music.stop()
                pygame.mixer.Sound.play(diesound)
            on = False
            pygame.mixer.music.stop()
            pygame.mixer.Sound.play(diesound)
        fullList = []
        XnY = []
        times = get_ticks()


        #Checks if laser has hit
        for i in range(len(hitting) - 1):

            if hitting[i] >= 0:

                #print(hitting)
                del laser_shoot[hitting[i]]
                #print(hitting)
                break

        #Laser
        if laser == True:
            laser = False
            laser_shoot.append([lead_x + 7, lead_y])
        for m in range(len(laser_shoot)):
            laser_shoot[m][1] = laser_shoot[m][1] - 7
            laser_x = laser_shoot[m][0]
            laser_y = laser_shoot[m][1]
            pygame.draw.rect(displayGame, red, [laser_x, laser_y, 3, 10])
        for m in range(len(laser_shoot)):
            if laser_shoot[m][1] < -10:
                laser_shoot.remove(laser_shoot[m])
                break
        where_duck = laser_shoot



        XnY, hitting, fullList, extrascore = score_summon(score, where_duck, lead_x, lead_y, extrascore)

        #Looks if DUCK hit LILY
        nr = 0
        if not die or die2 == False:
            for XnYs in fullList:
                nr += 1
                x = XnYs[0]
                y = XnYs[1]
                for m in [int(lead_x), int(lead_x) + block_size]:
                    if m > x and m < x + big_block_size:
                        for p in [int(lead_y), int(lead_y) + block_size]:
                            if p > y and p < y + big_block_size:
                                    die = True
                                    death_by_lilly_nr = XnYs[2]
                                    pygame.mixer.music.stop()
                                    pygame.mixer.Sound.play(diesound)

        #Print grass
        show_message("Score: " + str(score), red, 250, 250)
        displayGame.blit(grass, (0, 0))
        displayGame.blit(grass, (width - big_block_size, 0))
        pygame.display.update()

        clock.tick(100)


    show_message("You Lose", red)
    pygame.display.update()
    time.sleep(1)

    while True:

        show_message("Press Space to play again.", yellow, 50)
        pygame.display.update()

        for event in pygame.event.get():
            mouse = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN and ((500 + 200 > mouse[0] > 500) and (500 + 40 > mouse[1] > 500)):
                gameLoop2()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    gameExit = True
                    gameOver = False
                if event.key == pygame.K_SPACE:
                    pygame.mixer.music.play(-1)
                    gameLoop()
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        grey = (130, 130, 130)
        light_gray = (90, 90, 90)




        x, y, m, n = 495, 495, 210, 50
        t, l, u = 50, 50, 50
        for i in range(1, 11):
            t += 10
            l += 10
            u += 10
            grey = (t, l, u)
            pygame.draw.rect(displayGame, grey, [x, y, m, n])
            x += 1
            y += 1
            m -= 2
            n -= 2
        pygame.draw.rect(displayGame, grey, [500, 500, 200, 40])
        mouse = pygame.mouse.get_pos()
        if 500 + 200 > mouse[0] > 500 and 500 + 40 > mouse[1] > 500:
            pygame.draw.rect(displayGame, light_gray, [500, 500, 200, 40])

        grey = (45, 45, 45)

        show_message("Back to Menu", grey, -220, 200)
        pygame.display.update()

#init colors
white = (255, 255, 255)
black = (0, 0, 0)

grey = (110, 110, 110)
display_width = 800
display_height = 600
FPS = 15
#Make display
gameDisplay = pygame.display.set_mode((display_width, display_height))
#Title
pygame.display.set_caption('MeNu')
#Clock
font1 = pygame.font.SysFont(None, 53)
font2 = pygame.font.SysFont(None, 45)
font4 = pygame.font.SysFont(None, 75)

def message_to_screen4(msg, color, x=0, y=0):
    text = font4.render(msg, True, color)
    text_rect = text.get_rect(center=(display_width / 2 + x, display_height / 2 - y))
    gameDisplay.blit(text, text_rect)

def message_to_screen1(msg, color, x=0, y=0):
    text = font1.render(msg, True, color)
    text_rect = text.get_rect(center=(display_width / 2 + x, display_height / 2 - y))
    gameDisplay.blit(text, text_rect)

def message_to_screen2(msg, color, x=0, y=0):
    text = font2.render(msg, True, color)
    text_rect = text.get_rect(center=(display_width / 2 + x, display_height / 2 - y))
    gameDisplay.blit(text, text_rect)








def gameLoop2():
    # init variable
    gameExit = False


    #gameloop
    while not gameExit:

        for event in pygame.event.get():
            mouse = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN and (300+200 > mouse[0] > 300 and 230 + 40 > mouse[1] > 230):
                pygame.mixer.music.play(-1)
                gameLoop()
            if event.type == pygame.MOUSEBUTTONDOWN and (300+200 > mouse[0] > 300 and 350 + 40 > mouse[1] > 350):
                pygame.mixer.music.play(-1)
                print('dsa')
        gameDisplay.fill(blue)
        pygame.draw.rect(gameDisplay, green, [0, 0, display_width, 120])
        nr = 120
        clr = 155
        for i in range(1, 20):
            color = (0, clr, 0)
            pygame.draw.rect(gameDisplay, color, [0, nr, display_width, 1])
            nr += 1
            clr -= 3
        pygame.draw.rect(gameDisplay, black, [0, 139, display_width, 1])

        pygame.draw.rect(gameDisplay, green, [0, display_height-80, display_width, 80])
        nr = display_height-80
        clr = 155
        for i in range(1, 20):
            color = (0, clr, 0)
            pygame.draw.rect(gameDisplay, color, [0, nr, display_width, 1])
            nr -= 1
            clr -= 3
        pygame.draw.rect(gameDisplay, black, [0, display_height-100, display_width, 1])

        message_to_screen4("Lilypod Dodge Ultimate", black, -1, 231)
        message_to_screen4("Lilypod Dodge Ultimate", black, 1, 231)
        message_to_screen4("Lilypod Dodge Ultimate", black, -1, 229)
        message_to_screen4("Lilypod Dodge Ultimate", black, 1, 229)
        message_to_screen4("Lilypod Dodge Ultimate", red, 0, 230)

        grey = (130, 130, 130)
        light_gray = (90, 90, 90)


        x, y, m, n = 295, 225, 210, 50
        t, l, u = 50, 50, 50
        for i in range(1, 11):
            t += 10
            l += 10
            u += 10
            grey = (t, l, u)
            pygame.draw.rect(gameDisplay, grey, [x, y, m, n])
            x += 1
            y += 1
            m -= 2
            n -= 2

        x, y, m, n = 295, 345, 210, 50
        t, l, u = 50, 50, 50
        for i in range(1, 11):
            t += 10
            l += 10
            u += 10
            grey = (t, l, u)
            pygame.draw.rect(gameDisplay, grey, [x, y, m, n])
            x += 1
            y += 1
            m -= 2
            n -= 2

        grey = (130, 130, 130)
        pygame.draw.rect(gameDisplay, grey, [300, 230, 200, 40])
        pygame.draw.rect(gameDisplay, grey, [300, 350, 200, 40])

        mouse = pygame.mouse.get_pos()
        if 300+200 > mouse[0] > 300 and 230 + 40 > mouse[1] > 230:
            pygame.draw.rect(gameDisplay, light_gray, [300, 230, 200, 40])
        if 300+200 > mouse[0] > 300 and 350 + 40 > mouse[1] > 350:
            pygame.draw.rect(gameDisplay, light_gray, [300, 350, 200, 40])

        grey = (45, 45, 45)
        message_to_screen2("Single Player", grey, 0, 50)
        message_to_screen2("Multiplayer", grey, 0, -69)



        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()
    quit()

gameLoop2()



