from .diary import load_all
from datetime import date, timedelta

def view(date):
    entries = load_all()
    print(date)
    for line in entries[date]:
        print('- ' + str(line))
