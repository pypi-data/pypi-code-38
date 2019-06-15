from selenium import webdriver


def get_uid_string(ip):
    driver = webdriver.Firefox()
    uid = ""
    driver.get(f"{ip}:80")
    uid = driver.find_element_by_id("uidValue").text
    driver.close()
    return uid


def get_uid_long(ip):
    driver = webdriver.Firefox()
    uid = ""
    driver.get(f"{ip}:80")
    uid = driver.find_element_by_id("uidValue").text
    long_uid = int(uid)
    driver.close()
    return long_uid
