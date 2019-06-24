import re
import json
import requests
# import urllib3
import pkg_resources

from urllib.parse import urlencode


def clean_string(string):
    string = string.strip()
    string = string.replace("\n", " ")
    string = string.replace("\r", " ")
    string = re.sub(' +', ' ', string)
    return string


# write given list (results) to file at path
def write_list(path, results):
    print("write list to file", path)
    if type(results[0]) == str:
        with open(path, "w+", encoding="utf8") as f:
            f.write("\n".join(results))
    if type(results[0]) == list:
        with open(path, "w+", encoding="utf8") as f:
            for res in results:
                f.write('"' + '"\n"'.join(res) + '"\n')


def write_csv(path, results):
    print("write csv to file", path)
    with open(path, "w+", encoding="utf8") as f:
        for row in results:
            f.write('"' + '","'.join(row) + '"\n')


def read_csv_with_header(path):
    lines = read_plain_clean(path)
    header = lines[0].split(",")
    columns = []
    values = {}
    for name in header:
        columns.append(name.replace('"',''))
        values[name.replace('"','')] = []
    for row in lines[1:]:
        for i, v in enumerate(row.split(",", 1)):
            values[columns[i]].append(v.replace('"',''))
    return values


# read plain text file
def read_plain_clean(path):
    print("read plain text file", path)
    lines = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            lines.append(line.strip('\n'))
    return lines


# read json file at path
def read_json(path):
    print("read file", path)
    result = {}
    with open(path, 'r', encoding='utf-8') as f:
        result = json.load(f)
    return result


# write given data to json file at path
def write_json(path, data):
    print("write to", path)
    with open(path, 'w', encoding="utf-8") as f:
        s = json.dumps(data, indent=2)
        f.write(s)
    return path


# send get request to fetch data
def get_request(url, params=None, headers=None, json_response=True):
    if params:
        params = urlencode(params)
        url = url + params
    if headers:
        response = requests.get(url, headers=headers)
    else:
        response = requests.get(url)
    if response.status_code == 200:
        if json_response:
            return response.json()
        else:
            return response
    else:
        # print("something went wrong while requesting data!")
        print("got status code", response.status_code, "for url:\n", url)
        return {}


# send a post request with data
def post_request(url, params=None, headers=None, data=None, json_res=True):
    if params:
        params = urlencode(params)
        url = url + params
    if type(data) == dict:
        payload = json.dumps(data)
    else:
        payload = data
    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        if json_res:
            return response.json()
        else:
            return response
    else:
        # print("something went wrong while requesting data!")
        print("got status code", response.status_code, "for url:\n", url)
        return {}


# send a put request with data
def put_request(url, header, data):
    payload = json.dumps(data)
    response = requests.put(url, headers=header, data=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print("something went wrong while requesting data!")
        print("got status code", response.status_code, "for url:\n", url)
        return {}


user_agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) Gecko/20100101 Firefox/64.0'}


def check_url(url):
    try:
        response = requests.head(url)
    except Exception as e:
        print(str(e))
        print("... tried to access:", url)
        return ''
    if response.status_code == 200:
        # print("HTTP 200", url)
        return url
    elif response.status_code == 303:
        # print("HTTP 302", url)
        return response.headers['Location']
    elif response.status_code == 302:
        # print("HTTP 302", url)
        return response.headers['Location']
    elif response.status_code == 301:
        # print("HTTP 301", url)
        return response.headers['Location']  # check if 301 has new location
    elif response.status_code == 403:
        print("HTTP", response.status_code, url)
        print("could not check")
        return url
    elif response.status_code == 404:
        return ''
    else:
        print("HTTP", response.status_code, url)
        print("... unhandled status code!")
        return url


def url_exists(url):
    try:
        response = get_request(url, json_response=False, headers=user_agent)
    except Exception as e:
        print(str(e))
        print("while accessing", url)
        return False
    if not response:
        return False
    else:
        return True


def url_exists2(url):
    try:
        response = requests.head(url)
    except Exception as e:
        print(str(e))
        print("... tried to access:", url)
        return ''
    if response.status_code == 404:
        return False
    else:
        return True


# resolve path of package files
def resolve_path(path):
    return pkg_resources.resource_filename('pybman', path)
