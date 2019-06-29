from flask import Flask, request

PAUSE = 'pause'
CONTINUE = 'continue'


def task_manager(event):
    app = Flask(__name__)

    @app.route("/")
    def main():
        cmd = request.args.get('cmd')

        if cmd not in [PAUSE, CONTINUE]:
            raise ValueError()

        if cmd == PAUSE:
            if not event.is_set():
                return "Already pause"
            else:
                event.clear()

        elif cmd == CONTINUE:
            if event.is_set():
                return "Process is not paused"
            else:
                event.set()

        return 'OK'

    return app.run
