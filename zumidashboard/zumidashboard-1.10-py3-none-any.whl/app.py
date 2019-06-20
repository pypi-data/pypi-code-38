from flask import Flask, request, render_template
from flask_socketio import SocketIO
import time, subprocess
from zumi.zumi import Zumi
from zumi.personality import Personality
from zumi.util.screen import Screen
import zumidashboard.scripts as scripts
from zumidashboard.idle_animation import idle
import os

app = Flask(__name__, static_url_path="", static_folder='dashboard')
app.zumi = Zumi()
app.screen = Screen(clear=False)
app.p = Personality(app.zumi, app.screen)
app.ssid = ''
socketio = SocketIO(app)


@app.route('/')
@app.route('/index')
def index():
    return app.send_static_file('index.html')


@app.route('/select-network')
def select_network():
    return app.send_static_file('index.html')

@app.route('/shutting-down')
def shutting_down():
    return app.send_static_file('index.html')

@app.route('/step2')
def step2():
    return app.send_static_file('index.html')


@app.route('/update')
def update():
    return app.send_static_file('index.html')


@socketio.on('ssid_list')
def ssid_list(sid):
    print('getting ssid list')
    _list = scripts.get_ssid_list()
    socketio.emit('ssid_list',str(_list))


@socketio.on('connect_wifi')
def connect_wifi(ssid, passwd):
    print('app.py : connecting wifi start')
    print(ssid)
    scripts.add_wifi(ssid, passwd)
    print("personality start")
    app.p.attempt_connection()
    print("personality done")
    print('app.py : connecting wifi end')


# get rid of this event
@socketio.on('check_connection')
def check_connection():
    # print('app.py : check_connection start')
    # print('checking connection...')
    # connected, ssid = scripts.check_wifi()
    # if connected:
    #     print("personality start")
    #     app.p.connected_wifi(ssid)
    #     print("personality done")
    #     socketio.emit('check_connection', 'true')
    # else:
    #     app.screen.draw_text_center("Failed to connect.\n Try again.")
    #     socketio.emit('check_connection', 'false')
    # print('app.py : check_connection end')
    # socketio.emit('check_connection', 'true')
    pass


@socketio.on('check_internet')
def check_internet():

    connected, ssid = scripts.check_wifi()
    app.ssid = ssid
    connected_to_internet = scripts.check_internet()
    if connected and "zumidashboard" in connected_to_internet:
        socketio.emit('check_internet', connected_to_internet)
    else:
        app.screen.draw_text_center("Failed to connect.\n Try again.")
        socketio.emit('check_internet', '')


@socketio.on('zumi_success')
def zumi_success():
    app.p.connected_wifi(app.ssid)


@socketio.on('zumi_fail')
def zumi_success():
    app.screen.draw_text_center("Failed to connect.\n Try again.")


@socketio.on('run_demos')
def run_demos():
    print('Run demos event from dashboard')


@socketio.on('goto_lessons')
def goto_lessons():
    print('Go to lessons event from dashboard')


@socketio.on('update_firmware')
def update_firmware():
    print('update firmware from dashboard')
    print('server down soon')
    time.sleep(1)
    subprocess.run(["sudo killall -9 python3 && sudo python3 -c 'import zumidashboard.updater as update; update.run()'"], shell=True)


@app.route('/hostname')
def orig():
    return render_template('hostname.html')


@app.route('/result', methods=['POST'])
def change_host():
    host = request.form["host"]
    scripts.change_hostname(host)
    return "Changed"


@app.route('/idle')
def idle_test():
    idle(app.zumi, app.screen, app.p)
    return "Changed"


def run(_debug=False):
    if not os.path.isfile('/usr/local/lib/python3.5/dist-packages/zumidashboard/dashboard/hostname.json'):
        subprocess.run(["sudo ln -s /etc/hostname /usr/local/lib/python3.5/dist-packages/zumidashboard/dashboard/hostname.json"], shell=True)

    socketio.run(app, debug=_debug, host='0.0.0.0', port=80)


if __name__ == '__main__':
    run()
