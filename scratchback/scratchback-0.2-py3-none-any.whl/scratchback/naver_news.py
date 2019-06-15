from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import requests, time

# 네이버 뉴스 속보에서 날짜, 페이지 조건하에 크롤링합니다.
class NaverNews:
    def __init__(self, base_url = 'https://news.naver.com/main/list.nhn?mode=LSD&mid=sec&sid1=001', \
                 page_num = 1, page_start = 1, page_end = None,
                 date_start = None, date_end = None):
        
        # 기본 url = 네이버 속보
        self.base_url = base_url
        # 날짜별 긁어올 페이지 수
        self.page_num = page_num
        self.news_list = []
        # start 날짜를 입력하지 않으면 오늘 날짜로 자동 지정됩니다.
        self.date_start = date_start
        # end 날짜를 입력하지 않으면 오늘 날짜로 자동 지정됩니다..
        self.date_end = date_end
        
        self.page_end = page_end
        self.page_start = page_start
        
        self.description = \
        """
        DS School 프로그래밍 입문반의 네이버 뉴스 속보 크롤러입니다.
        """
        
        # 날짜를 따로 지정하지 않으면 오늘 날짜를 반환
        if self.date_start == None:
            self.date_start = datetime.strftime(datetime.now().date(), "%Y.%m.%d")
        if self.date_end == None:
            self.date_end = datetime.strftime(datetime.now().date(), "%Y.%m.%d")

            
        if datetime.strptime(self.date_start, "%Y.%m.%d").date() > datetime.now().date():
            self.date_start = datetime.strftime(datetime.now().date(), "%Y.%m.%d")
            
        if datetime.strptime(self.date_end, "%Y.%m.%d").date() > datetime.now().date():
            self.date_end = datetime.strftime(datetime.now().date(), "%Y.%m.%d")
            
        
        
       
        assert datetime.strptime(self.date_end, "%Y.%m.%d").date() >= datetime.strptime(self.date_start, "%Y.%m.%d").date()
        assert self.page_num > 0
        if page_end != None:
            assert self.page_end >= self.page_start
            assert (self.page_end - self.page_start + 1) == self.page_num
        
        
    def crawl(self):
    
        str_date_list = self.get_date_list()
        
        for date in str_date_list:
            
            # 날짜에 존재하는 최대 페이지수 가져오기
            max_page = self.find_max_page(date)
            
            
            page_e = self.page_end
            page_s = self.page_start
            
            
            # 끝 페이지가 None 경우 지정해주기
            if page_e == None :
                page_e = page_s + self.page_num - 1
                
            
            # 끝 페이지가 최대 페이지보다 큰 경우 최대 페이지로 지정
            if page_e > max_page :
                page_e = max_page
        
            if page_s > max_page :
                page_s = max_page
            
            
            num = 1
            for page in range(page_s, page_e + 1):
                
                print(f"Crawling page {page} of {date}...")
                url = self.base_url + '&date=' + date + '&page=' + str(page)
                
                response = requests.get(url)
                assert response.ok
                
                html = response.text
                
                # 잘못된 url, 빈 페이지 처리
                assert '페이지를 찾을 수 없습니다' not in html
                assert html != ''
                
                bs = BeautifulSoup(html, 'html.parser')
                
                # url
                url_tag = bs.select('.newsflash_body .type06_headline li dl')
                page_url_list = [tag.a.get('href') for tag in url_tag]
                
                for url in page_url_list:
                    
                    news = {}
                    time.sleep(0.01)
                    
                    response = requests.get(url)
                    assert response.ok

                    html = response.text
                    bs = BeautifulSoup(html, 'html.parser')
                    

                    # 헤드 라인
                    headline_tag = bs.find_all('h3', {'id': 'articleTitle'}, {'class': 'tts_head'})
                    headline = headline_tag[0].text
                    news['headline'] = headline
                    
                    # 기사 본문
                    content_tag = bs.select_one('div > #articleBodyContents')
                    content = self.clean_content(content_tag)
                    news['content'] = content
                    
                    # 날짜 
                    news['written at'] = datetime.strptime(date, "%Y%m%d").date()
                    
                    # 신문사
                    company_tag = bs.find_all('meta', {'property': 'me2:category1'})
                    company = company_tag[0].get('content')
                    news['company'] = company

                    # url
                    news['url'] = url
                    
                    # 뉴스 순서
                    news['title'] = f'{num}번째 뉴스'
                    
                    # id
                    oid = url.split("&")[-2].split("=")[-1]
                    aid = url.split("&")[-1].split("=")[-1]

                    nid = oid + '-' + aid
                    news['id'] = nid
                    
                    self.news_list.append(news)
                    
                    num += 1
        
        
        print(f"{len(self.news_list)} news were crawled")
        
        return self.news_list
            
    # 기사 본문 내용을 클리닝합니다.
    def clean_content(self, content_tag):
        content = ''
        for item in content_tag.contents:
            text = str(item)
            stripped = text.strip()
            if stripped == '':
                continue
            if stripped[0] not in ["<", "/"]:
                content += text.strip()
        content = content.replace("본문 내용TV플레이어", "")
        
        return content
    
    
    # 날짜를 지정하면 20190601식으로 리스트를 반환합니다.
    def get_date_list(self):
        
        date_list = []
        s_date = datetime.strptime(self.date_start, "%Y.%m.%d")
        e_date = datetime.strptime(self.date_end, "%Y.%m.%d")
        time_range = (e_date - s_date).days
        for day in range(time_range + 1):
            date = s_date + timedelta(days = day)
            date = date.date()
            year = str(date.year)
            month = date.month
            day = date.day
            
            if date.month >= 10:
                month = str(month)
            else : 
                month = '0' + str(month)
                
            if date.day >= 10:
                day = str(day)
            else :
                day = '0' + str(day)
                
            date = year + month + day
            date_list.append(date)
        date_list.reverse()
            
        return date_list
    
    # 날짜별 최대 페이지 수를 찾습니다.
    def find_max_page(self, date) :
        url = self.base_url + '&date=' + date + '&page=10000'
        response = requests.get(url)
        assert response.ok
        html = response.text
        bs = BeautifulSoup(html, 'html.parser')
        tag = bs.select("div.paging")
        max_page = int(tag[0].text.strip().split('\n')[-1])
        
        return max_page
    
