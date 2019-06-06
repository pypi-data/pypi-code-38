import firebase_admin
from firebase_admin import firestore, credentials
import os


class Firestore:
    def __init__(self):
        cred = credentials.Certificate(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
        firebase_admin.initialize_app(cred)
        self.fs_client = firestore.client()
