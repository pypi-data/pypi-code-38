import unittest, sys

def main():
    suite = unittest.TestLoader().discover('.', pattern = "*_test.py")
    results = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(not results.wasSuccessful())

if __name__ == "__main__":
    main()