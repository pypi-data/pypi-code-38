from os.path import join

def screenshots(driver, screenshot_dir, name):
 
    driver.get_screenshot_as_file(join(screenshot_dir, '{0}.png'.format(name)))
  
    with open(join(screenshot_dir, '{0}.html.log'.format(name)), "w") as f:
        f.write(driver.page_source.encode("utf-8"))
