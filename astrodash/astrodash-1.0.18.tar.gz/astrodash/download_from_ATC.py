from selenium import webdriver
import time
import pandas as pd

USERNAME = 'USERNAME'
PASSWORD = 'PASSWORD!'


def login_to_atc():
    browser = webdriver.Chrome()
    browser.get('https://portal-auth.nersc.gov/atc2/web/targets/DES16X2gap')
    time.sleep(10)
    username = browser.find_element_by_id("j_username")
    password = browser.find_element_by_id("j_password")
    username.send_keys(USERNAME)
    password.send_keys(PASSWORD)
    login_attempt = browser.find_element_by_xpath("//*[@type='submit']")
    login_attempt.submit()
    time.sleep(10)
    return browser


def open_page_and_download_spectrum(browser, objectName):
    browser.get('https://portal-auth.nersc.gov/atc2/web/spectra/' + objectName)
    time.sleep(10)
    downloaded = False
    files = []
    elems = browser.find_elements_by_xpath("//a[@href]")
    for elem in elems:
        if '/spectrum/' in elem.get_attribute("href"):
            fileToDownload = elem.get_attribute("href")
            files.append(fileToDownload)
            linkText = elem.get_attribute("innerText")
            if 'aat' not in linkText:
                print(linkText, fileToDownload)
                browser.get(fileToDownload)
                downloaded = True
    if not downloaded and files != []:
        browser.get(files[0])


def get_object_names(filename):
    df = pd.read_csv(filename, sep=',', header=1)
    ozdesList = df.values
    names = ozdesList[:, 1]
    numTransients = len(names)
    return names


if __name__ == '__main__':
    names = get_object_names('91bg_candidates.csv')
    browser1 = login_to_atc()
    for name in names:
        open_page_and_download_spectrum(browser1, name)
    # browser1.close()
