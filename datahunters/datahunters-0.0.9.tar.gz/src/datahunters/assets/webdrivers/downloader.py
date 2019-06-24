"""Web driver downloader.
"""

import os
import platform
import urllib
import stat
import tarfile
import zipfile


def download_chrome_driver():
  linux_url = "https://chromedriver.storage.googleapis.com/2.34/chromedriver_linux64.zip"
  mac_url = "https://chromedriver.storage.googleapis.com/2.34/chromedriver_mac64.zip"
  win_url = "https://chromedriver.storage.googleapis.com/2.34/chromedriver_win32.zip"
  cur_dir = os.path.dirname(os.path.realpath(__file__))
  save_dir = os.path.join(cur_dir, "chrome")
  if not os.path.exists(save_dir):
    os.makedirs(save_dir)
  data_fn = os.path.join(save_dir, "driver.zip")
  if platform.system() == "Linux":
    download_url = linux_url
  elif platform.system() == "Darwin":
    download_url = mac_url
  else:
    download_url = win_url
  print("downloading chrome driver, this may take some time...")
  filepath, _ = urllib.request.urlretrieve(download_url, data_fn)
  statinfo = os.stat(filepath)
  print("Successfully downloaded", data_fn, statinfo.st_size, "bytes.")
  print("unzipping...")
  zip_ref = zipfile.ZipFile(data_fn, "r")
  zip_ref.extractall(save_dir)
  zip_ref.close()
  os.remove(data_fn)
  # change permission.
  driver_fn = os.path.join(save_dir, "chromedriver")
  st = os.stat(driver_fn)
  os.chmod(driver_fn, st.st_mode | stat.S_IEXEC)
  print("finished.")


def download_phantom_driver():
  linux_url = "https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2"
  mac_url = "https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-macosx.zip"
  win_url = "https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-windows.zip"
  cur_dir = os.path.dirname(os.path.realpath(__file__))
  save_dir = os.path.join(cur_dir, "phantom")
  if not os.path.exists(save_dir):
    os.makedirs(save_dir)
  if platform.system() == "Linux":
    data_fn = os.path.join(save_dir, "driver.tar.bz2")
    download_url = linux_url
  else:
    data_fn = os.path.join(save_dir, "driver.zip")
    download_url = mac_url
  print("downloading phantom driver, this may take some time...")
  filepath, _ = urllib.request.urlretrieve(download_url, data_fn)
  statinfo = os.stat(filepath)
  print("Successfully downloaded", data_fn, statinfo.st_size, "bytes.")
  print("unzipping...")
  if platform.system() == "Linux":
    tarfile.open(data_fn, 'r:bz2').extractall(save_dir)
  else:
    zip_ref = zipfile.ZipFile(data_fn, "r")
    zip_ref.extractall(save_dir)
    zip_ref.close()
  os.remove(data_fn)
  print("finished.")


def download_all_drivers():
  download_chrome_driver()
  download_phantom_driver()


if __name__ == "__main__":
  # download_chrome_driver()
  download_phantom_driver()
