import locale

from quandoo.QuandooModel import QuandooModel


class Customer(QuandooModel):

    def __init__(self, data, agent):
        self.id = data["id"]
        self.firstName = data["firstName"]
        self.lastName = data["lastName"]
        self.email = data["email"]
        self.phoneNumber = data["phoneNumber"]

        super().__init__(data)

    def to_json(self):
        return {
            "firstName": self.firstName,
            "lastName": self.lastName,
            "emailAddress": self.email,
            "phoneNumber": self.phoneNumber,
            "locale": locale.getdefaultlocale()[0],
            "country": locale.getdefaultlocale()[0][-2:]
        }
