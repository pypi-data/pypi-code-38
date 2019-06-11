from PySide2.QtWidgets import QDesktopWidget
from PySide2.QtWidgets import QVBoxLayout, QBoxLayout, QGridLayout, QLayout
from networktools.colorprint import gprint, bprint, rprint


def read_css(file_name):
    print("Reading css")
    try:
        file_path = "./estilos/%s.css" % file_name
        with open(file_path, 'r') as f:
            content = f.read()
            return content
    except:
        return None


def print_dict(msg):
    print("==="*10)
    print("Data recibida  Qs2g")
    [print(k, v) for k, v in msg.items()]
    print("==="*10)


def center_window(window):
    window.move(QDesktopWidget().availableGeometry().center() -
                window.frameGeometry().center())


def set_layout(widget, layout=None):
    if issubclass(type(layout), QLayout):
        widget.setLayout(layout)
    else:
        widget.setLayout(QGridLayout())


def read_queue(queue, callback=print_dict):
    """
    Read from socket to gui,
    Execute the callback with the received msg
    """
    try:
        if not queue.empty():
            for i in range(queue.qsize()):
                msg_in = queue.get()
                if msg_in:
                    callback(msg_in)
                queue.task_done()
    except Exception as ex:
        print("Error con modulo de escritura de cola", queue)
        raise ex
