

# class UserIsNotLoggedInError(Exception):
#     def __init__(self, userName):
#         self.userName = userName
#
#     def __str__(self):
#         return "User %s is not logged in on any device" % self.userName


class UserIsNotLoggedInToThisDeviceError(Exception):
    def __init__(self, userName):
        self.userName = userName

    def __str__(self):
        return "User %s is not logged into this device" % self.userName


class UserNotFoundException(Exception):
    def __init__(self, userName):
        self.userName = userName

    def __str__(self):
        if self.userName is None:
            return "User name not selected"
        else:
            return "User %s is not found in database" % self.userName



class UserPasswordNotSetException(Exception):
    def __init__(self, userName):
        self.userName = userName

    def __str__(self):
        if self.userName is None:
            return "UserPasswordNotSetException:User name not selected"
        else:
            return "No password set for user %s" % self.userName
