from os.path import expanduser
home=expanduser("~")

def music_playlists(pages=5,filepath=home+'/163ranking_playlists.json'):
    '''
    para:   pages        how many pages are you gonna get
    para:   filepath    filepath to get the results, as in json
    '''
    import json
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.wait import WebDriverWait

    driver=webdriver.Chrome()

    url='https://music.163.com/#/discover/playlist/?order=hot&cat=全部&limit=35&offset=0'

    def next_page():
        next_button=driver.find_element(By.CLASS_NAME,'znxt')
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
        next_button.click()
        page_ready()

    def page_ready():
        wait=WebDriverWait(driver,10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME,'znxt')))

    def load_homepage(url):
        driver.get(url)
        wait=WebDriverWait(driver,10)
        wait.until(EC.presence_of_element_located((By.NAME,'contentFrame')))
        driver.switch_to.frame('contentFrame')
        page_ready()

    def main():
        load_homepage(url)
        playlists=[]

        for i in range(1,pages+1):
            print(driver.current_url)
            playlist=driver.find_elements(By.CLASS_NAME, 'msk')
            one=[{"title":item.get_attribute('title'),"url":item.get_attribute('href')} for item in playlist]
            playlists.append(one)
            next_page()


        if json.dump(playlists,open(filepath,'w',encoding='utf-8'),ensure_ascii=False):
            print('all done')
    try:
        main()

    finally:
        driver.close()



