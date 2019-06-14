import unittest
import os
from firstclass_dotenv import Dotenv

class Test1stclassDotenv(unittest.TestCase):
  def test_init(self):
    print("test __init__")
    dotenv = Dotenv()
    dotenv.load()
    assert os.environ["envfile"] == ".env", ".env file is missing"

  def test_setDotenv(self):
    print("test setDotenv()")
    dotenv = Dotenv()
    dotenv.load(os.path.dirname(os.path.abspath(__file__)) + "/.env.specified1")
    assert os.environ["envfile"]==".env.specified1", ".env.specified1 env file is missing"

  def test_setDotenv_by_contructor(self):
    print("test setDotenv_by_contructor")
    dotenv = Dotenv(os.path.dirname(os.path.abspath(__file__)) + "/.env.specified2")
    dotenv.load()
    assert os.environ["envfile"] == ".env.specified2", ".env.specified2 env file is missing"

if __name__ == "__main__":
  unittest.main()
