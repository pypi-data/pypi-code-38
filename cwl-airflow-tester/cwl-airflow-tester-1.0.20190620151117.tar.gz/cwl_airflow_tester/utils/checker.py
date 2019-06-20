import threading
import logging
import socketserver
import queue
import shutil
from http.server import SimpleHTTPRequestHandler
from json import loads, dumps
from cwltest.utils import compare, CompareFail

from cwl_airflow_tester.utils.mute import Mute


RESULTS_QUEUE = None


class CustomHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        with Mute():
            self.send_response(200)
        self.end_headers()
        if "status" in self.path:
            return None
        payload = loads(self.rfile.read(int(self.headers['Content-Length'])).decode("UTF-8"))["payload"]
        if payload.get("results", None) or payload.get("state", None) == "failed":
            logging.debug(f"""   got updates from {self.path}:\n{dumps(payload, indent=4)}""")
            RESULTS_QUEUE.put({
                "run_id":  payload["run_id"],
                "dag_id":  payload["dag_id"],
                "results": payload.get("results", None)
            })


def get_listener_thread(queue, port, daemon):
    global RESULTS_QUEUE
    RESULTS_QUEUE = queue
    httpd = socketserver.TCPServer(("", port), CustomHandler)
    return threading.Thread(target=httpd.serve_forever, daemon=daemon)


def evaluate_result(data):
    processed = 0
    while processed < len(data):
        try:
            item = RESULTS_QUEUE.get()
        except queue.Empty:
            continue
        processed = processed + 1
        try:
            compare(data[item["run_id"]]["output"], item["results"])
            logging.error(f"""\nSuccess   {item["dag_id"]}: {item["run_id"]}""")
        except CompareFail as ex:
            data[item["run_id"]]["error"] = str(ex)
            logging.error(f"""\nFail      {item["dag_id"]}: {item["run_id"]}""")
            logging.debug(f"""{data[item["run_id"]]["error"]}""")
        finally:
            try:
                output_folder = data[item["run_id"]]["output_folder"]
                shutil.rmtree(output_folder)
                logging.debug(f"""Delete output directory {output_folder}""")
            except Exception as ex:
                logging.error(f"""Failed to delete temporary output directory \n{ex}""")


def get_checker_thread(data, daemon):
    return threading.Thread(target=evaluate_result,
                            daemon=daemon,
                            kwargs={"data": data})
