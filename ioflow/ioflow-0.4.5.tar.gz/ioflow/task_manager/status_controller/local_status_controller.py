from flask import Flask, request

from ioflow.task_manager.status_controller.status_controller_base import \
    StatusControllerBase


class LocalStatusController(StatusControllerBase):
    def main(self, pause_event, stop_event):
        app = Flask(__name__)

        @app.route("/")
        def main():
            cmd = request.args.get('cmd')

            self.exec(cmd, pause_event, stop_event)

            return 'OK'

        app.run()
