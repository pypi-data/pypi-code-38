import getpass

class Actions(object):

  @staticmethod
  def __prompt_username_password():
    u = input("Username: ")
    p = getpass.getpass(prompt="Password: ")
    return (u, p)

  @staticmethod
  def login(driver, username=None, password=None):
    if not username or not password:
      username, password = __prompt_username_password()
