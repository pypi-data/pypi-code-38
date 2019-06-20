from random import randint
from time import sleep, time
from threading import Thread


def idle(zumi, screen, personality):
    while True:
        # Timer code (sleep after ~60 seconds)
        timeout_for_sleeping = 60
        init = time()
        global is_sleeping
        is_sleeping = False
        while (time()-init) < timeout_for_sleeping:
            screen.hello()
            rand_func = randint(0, 8)

            if rand_func == 0:
                personality.happy()

            if rand_func == 1:
                personality.look_around_open()

            if rand_func == 2:
                angles_now_list = zumi.update_angles()
                angle_z = angles_now_list[2]
                zumi.turn(angle_z + randint(-45, 45), 2, max_speed=10, accuracy=5)

            if rand_func == 3:
                angles_now_list = zumi.update_angles()
                angle_z = angles_now_list[2]
                zumi.forward(5, 0.5, angle_z + randint(-10,10))
                zumi.stop(0)

            if rand_func == 4:
                angles_now_list = zumi.update_angles()
                angle_z = angles_now_list[2]
                zumi.reverse(speed=15, duration=0.6)

            if rand_func == 5:
                personality.celebrate()

            if rand_func == 6:
                Thread(target=personality.sound.blink).start()
                screen.close_eyes()
                screen.hello()

            if rand_func == 7:
                Thread(target=personality.sound.blink).start()
                screen.draw_image_by_name("lookleft1")
                sleep(1)
            if rand_func == 8:
                Thread(target=personality.sound.blink).start()
                screen.draw_image_by_name("lookright1")
                sleep(1)

            screen.hello()
            sleep(randint(2, 6))

        sleep(1)
        screen.draw_text("*yawn*", x=30, y=25, font_size=18)
        sleep(2)

        def sleeping_thread():
            if is_sleeping:
                screen.sleeping()

        tap_threshold = 0.3
        is_sleeping = True
        sleep_thread = Thread(target=sleeping_thread)
        sleep_thread.start()

        while is_sleeping:
            mpu_list = zumi.mpu.read_all_MPU_data()
            # convert into m/s**2
            x_acc = mpu_list[0]

            tilt = zumi.get_tilt(mpu_list[0], mpu_list[1], mpu_list[2])
            if (tilt[0] == 5):

                if (abs(x_acc) > tap_threshold):
                    print("tapped ", tilt[0], ",", x_acc)
                    zumi.play_note(60, 30)
                    is_sleeping = False
                    screen.disp.clear()
                    screen.disp.display()
                    sleep(0.2)

if __name__ == '__main__':
    from zumi.zumi import Zumi
    from zumi.util.screen import Screen
    from zumi.personality import Personality
    z = Zumi()
    s = Screen()
    p = Personality(z,s)
    idle(z,s,p)
