from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
import time
import unittest



class Instagram():

    
    def __init__(self, driver_path, headless = True):
        
        self.driver = None
        
        if headless:
            options = webdriver.ChromeOptions()
            options.add_argument('headless')
            options.add_argument("--start-maximized")
            options.add_argument("disable-gpu")

            try:
                driver = webdriver.Chrome(driver_path, options=options)
                driver.maximize_window()
                self.driver = driver
            except:
                print("Install Selenium or Check driver path.")
            
        else:
            try:
                driver = webdriver.Chrome(driver_path)
                driver.maximize_window()
                self.driver = driver
            except:
                print("Install Selenium or Check driver path.")
            
    def get_posts(self):
        soup = BeautifulSoup(self.driver.page_source, "lxml")
        post_num = int(soup.select_one("section > main > div > header > section > ul > li:nth-of-type(1) > a > span").get_text().replace(",", ""))
        return post_num

    def scroll_down(self):
        SCROLL_PAUSE_TIME = 1
        end_flag = True

        last_height = self.driver.execute_script("return document.body.scrollHeight")

        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)

        new_height = self.driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            attempt = 3
            while attempt > 0:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    attempt -= 1
                else:
                    attempt = 0
            
            if new_height == last_height:
                end_flag = False
        
        
        last_height = new_height

        return end_flag

    
    def get_video(self, soup, media_list):
        video_list = soup.select_one("div._97aPb").find_all("video")
        for video in video_list:
            src = video["src"]
            if src not in media_list:
                media_list.append(src)
        return media_list
        
    def get_img(self, soup, media_list):
        img_list = soup.select_one("article > div._97aPb").find_all("img", {"class" : "FFVAD"})
        for img in img_list:
            src = img["src"]
            if src not in media_list:
                media_list.append(src)
        return media_list
    
    def get_text(self, soup):
        
        text_list = [text.get_text() for text in soup.select_one("article > div.eo2As > div > ul > li").select("div > div > div.C4VMK > span")]
        
        return text_list
    
    
    def content(self, result, completed, posts, start_time):
        
        SCROLL_PAUSE_TIME = 0.5
        buttons = self.driver.find_elements_by_css_selector("article > div:nth-of-type(1) > div > div > div > a")

        for button in buttons:

            img_list = []
            if button in completed:
                continue

            hover = ActionChains(self.driver).move_to_element(button)
            hover.perform()
#             time.sleep(0.3)
            

            soup = BeautifulSoup(self.driver.page_source, "lxml")

            if len(result) % 3 == 0:
                comments = ""
            else:
                prev_comments = soup.select("article > div > div > div > div > a > div.qn-0x > ul > li")[1].get_text()
                result[-1]["comments"] = prev_comments
                
                comments = soup.select("article > div > div > div > div > a > div.qn-0x > ul > li")[-1].get_text()
                
                
            button.click()
            time.sleep(SCROLL_PAUSE_TIME)
            right_button = self.driver.find_elements_by_css_selector("button._6CZji > div.coreSpriteRightChevron")
            
            if len(right_button) == 0:
                attempt = 3
                while attempt > 0:
                    time.sleep(SCROLL_PAUSE_TIME)
                    right_button = self.driver.find_elements_by_css_selector("button._6CZji > div.coreSpriteRightChevron")
                    attempt = 0
                
            
            
            while len(right_button) != 0:
                
                soup = BeautifulSoup(self.driver.page_source, "lxml")

                attempt = 10
                while attempt > 0:
                    try:
                        img_list = self.get_video(soup, img_list)
                        img_list = self.get_img(soup, img_list)
                        attempt = 0
                    except:
                        time.sleep(5)
                        soup = BeautifulSoup(self.driver.page_source, "lxml")
                        attempt -= 1

                
                right_button[0].click()
                time.sleep(SCROLL_PAUSE_TIME)
                
                right_button = self.driver.find_elements_by_css_selector("button._6CZji > div.coreSpriteRightChevron")
                
                if len(right_button) == 0:
                    attempt = 3
                    while attempt > 0:
                        time.sleep(0.1)
                        right_button = self.driver.find_elements_by_css_selector("button._6CZji > div.coreSpriteRightChevron")
                        if len(right_button) == 0:
                            attempt -= 1
                        else:
                            attempt = 0
            
            soup = BeautifulSoup(self.driver.page_source, "lxml")
            attempt = 10
            text_list = []
            while attempt > 0:
                try:
                    text_list = self.get_text(soup)
                    attempt = 0
                except:
                    time.sleep(2)
                    soup = BeautifulSoup(self.driver.page_source, "lxml")
                    attempt -= 1
            
            
            attempt = 10
            while attempt > 0:
                try:
                    img_list = self.get_video(soup, img_list)
                    img_list = self.get_img(soup, img_list)
                    attempt = 0
                except:
                    time.sleep(5)
                    soup = BeautifulSoup(self.driver.page_source, "lxml")
                    attempt -= 1
            
            
            try:
                like_num = soup.select_one("article > div > section > div > div > button > span").get_text()
            except:
                try:
                    like_num = soup.select_one("article > div.eo2As > section > div > span").get_text()
                except:
                    like_num = ""

            if len(text_list)!= 0:
                content = ' '.join(text_list)
            else:
                content = ""

            self.driver.execute_script("window.history.go(-1)")

            completed.append(button)
            result.append({"content" : content, "img_src" : img_list, "like" : like_num, "comments" : comments})
            
            tmp = len(result)
            
            if tmp == posts:
                return result, completed
            current_time = time.time()
            print(f"{tmp} out of {posts} posts are crawled. {((current_time - start_time) // 60):.0f} minutes {(current_time - start_time) % 60:.0f} seconds passed.")

            
            
            
        return result, completed
    
    
    def crawl(self, account_name, posts=-1):
        
        SCROLL_PAUSE_TIME = 1
        start_time = time.time()

        self.url = f"https://www.instagram.com/{account_name}/"
        self.driver.get(self.url)
        
        time.sleep(SCROLL_PAUSE_TIME)
        
        total_posts = self.get_posts()
        if posts == -1:
            posts = total_posts
        
        if posts > total_posts:
            print(f"There are only {total_posts} posts. Changing number of posts to {total_posts}...")
            posts = total_posts
        
        end_flag = True
        result = []
        completed = []
        while end_flag and (len(result) != posts):
            attempt = 10
            while attempt > 0:
                try:
                    result, completed = self.content(result, completed, posts, start_time)
                    tmp = len(result)
                    end_flag = self.scroll_down()
                    attempt = 0
                except:
                    attempt -= 1
        
        
        if len(result) != posts:
            result, completed = self.content(result, completed, posts, start_time)
        self.driver.close()
        
        
        
        print(f"{len(result)} out of {posts} posts are crawled.")
        
        print("Crawling Completed!")
        
        return result
