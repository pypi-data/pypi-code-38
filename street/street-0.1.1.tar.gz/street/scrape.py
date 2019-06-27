from bs4 import BeautifulSoup
import pandas as pd
import requests

from .config import get_config
from .exceptions import RequestBlocked, EarningsTableNotFound


REFERER = 'https://www.google.com/'

def scrape(ticker_symbol):
    url = f'https://www.streetinsider.com/ec_earnings.php?q={ticker_symbol}'

    user_agent, cookie = get_config()
    headers = {
        'User-Agent': user_agent,
        'Referer': REFERER,
        'Cookie': cookie,
    }

    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        raise RequestBlocked

    page = r.text
    soup = BeautifulSoup(page, 'lxml')

    tables = soup.find_all('table', {'class': 'earning_history'})
    if not tables:
        raise EarningsTableNotFound


    data = []
    for table in tables:
        rows = table.find_all('tr', {'class': 'is_hilite'})
        for row in rows:
            cells = row.find_all('td')
            row_text = [cell.text for cell in cells]
            data.append(row_text)
    earn = pd.DataFrame(data)

    dropped_cols = [1, 8, 9, 10, 11]
    earn = earn.drop(dropped_cols, axis=1)

    renamed_cols = {
        0: 'DATE',
        2: 'QTR',
        3: 'EPS',
        4: 'EPS_CONSENSUS',
        5: 'SURPRISE',
        6: 'REVENUE',
        7: 'REVENUE_CONSENSUS',
    }
    earn = earn.rename(index=str, columns=renamed_cols)

    earn['DATE'] = pd.to_datetime(earn['DATE'])
    earn = earn.sort_values('DATE', ascending=False)

    return earn
