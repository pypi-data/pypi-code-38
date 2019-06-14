from Homevee import Homevee
from Homevee.Manager.UserManager import UserManager
from Homevee.Utils.Database import Database


class TestDataGenerator:
    def __init__(self):
        self.db = Database()
        return

    def generate_test_data(self):
        self.clear_database()

        Homevee().add_user(username="testadmin", password="testpw", is_admin=True)

        admin_user = UserManager().fin

        self.generate_data()

    def clear_database(self):
        pass

    def generate_test_data(self):
        pass