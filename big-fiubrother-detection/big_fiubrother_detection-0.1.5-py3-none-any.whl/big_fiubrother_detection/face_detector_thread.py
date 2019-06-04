import threading

class FaceDetectorThread(threading.Thread):

    def __init__(self, face_detector):
        threading.Thread.__init__(self)

        self.end_event = threading.Event()

        self.face_detector_object = face_detector

        self.image_event = threading.Event()
        self.image = None

        self.rects_event = threading.Event()
        self.rects = []

    def run(self):

        while not self.end_event.is_set():

            # Espero a que me pasen una imagen
            self.image_event.wait()

            if self.end_event.is_set():
                return

            # Bloqueo los bounding boxes
            self.rects_event.clear()
            self.rects = self.face_detector_object.detect_face_image(self.image)
            print("Found " + str(len(self.rects)) + " faces")

            # Libero imagen
            self.image_event.clear()

            # Libero bounding boxes
            self.rects_event.set()

    def stop(self):
        self.end_event.set()
        self.image_event.set()

    def set_image(self, img):
        if not self.image_event.is_set():
            self.image = img
            self.image_event.set()
            return True
        return False

    def rects_ready(self):
        return self.rects_event.is_set()

    def get_rects(self):
        if self.rects_event.is_set():
            self.rects_event.clear()
            return self.rects