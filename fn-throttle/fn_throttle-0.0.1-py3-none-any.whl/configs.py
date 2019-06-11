import os

# path
CURRENT_PATH = os.path.split(os.path.realpath(__file__))[0]
DATA_ROOT = os.path.join(CURRENT_PATH, 'data')

# web
PORT_CHOICES = (6000, 6050, 7000, 7050, 8000, 8050, 9000, 9050, 10000, 10050)
