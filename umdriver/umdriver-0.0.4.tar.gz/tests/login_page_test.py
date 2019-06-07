import pytest
from selenium.webdriver import ChromeOptions
from driver import UMDriver
from driver.pages import LoginPage


@pytest.fixture(scope='module')
def headlesschromedriver():
    opts = ChromeOptions()
    opts.headless = True
    opts.add_argument('--disable-gpu')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--window-size=1420,1080')
    opts.add_argument('--log-level=3')
    d = UMDriver(driver='chrome',
                 executable_path='/webdrivers/chromedriver.exe',
                 service_log_path='NUL',
                 chrome_options=opts)
    yield d
    d.quit()

@pytest.fixture
def chromedriver():
    opts = ChromeOptions()
    d = UMDriver(driver='chrome',
                 executable_path='/webdrivers/chromedriver.exe',
                 chrome_options=opts)
    yield d
    d.quit()

@pytest.fixture
def phantomjsdriver():
    d = UMDriver('phantomjs', executable_path='/webdrivers/phantomjs.exe')
    d.get('https://weblogin.umich.edu')
    yield d
    d.quit()

@pytest.fixture
def login_page(chromedriver):
    return LoginPage.get(chromedriver)

def test_username(login_page):
    username = 'test_username'
    login_page.username = username
    assert login_page.username == username

def test_password(login_page):
    password = '12345'
    login_page.password = password
    assert login_page.password == password

def test_username_and_password(login_page):
    username = '1234'
    password = '5678'
    login_page.username = username
    login_page.password = password
    assert login_page.username == username
    assert login_page.password == password

def test_error_msg_hidden(login_page):
    assert login_page.error_msgs == []

def test_error_msg_is_present(login_page):
    login_page.username = '1234'
    login_page._submit()
    assert 'Please enter your password' in login_page.error_msgs
