from bs4 import BeautifulSoup
import warnings; warnings.filterwarnings("ignore")
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from IPython.display import clear_output
import re, os, time, pickle, errno
import pandas as pd
import numpy as np
import threading

class BigwingCrawler():

    def __init__(self, url='about:blank', page_range=None, page_type=None, browser='Chrome', headless=True, n_jobs=1, verbose=True):
        '''
        크롤러 클래스 생성자
        :param url:
        :param browser: 헤드리스 브라우저 지정 Chrome(Default) or PhantomJS
        :param headless: 헤드리스 모드 설정 True(Default) or False
        '''
        try :
            self.url = url
            self.page_type = page_type
            self.browser = browser
            self.headless = headless
            self.n_jobs = n_jobs
            self.data = None
            self.thread = []
            self.verbose = verbose
            if page_range != None:
                self.partitioner(page_range[0], page_range[1], n_jobs)
                self.start_page = page_range[0]
                self.end_page = page_range[1]

            self.error_page_list = self.load("error_pages")
            self.success_page_list = self.load("success_pages")

        except Exception as e:
            print(e)
            self.close()


    def partitioner(self, start, end, divide):

        partition_sp = np.linspace(start - 1, end, divide + 1).astype(int)

        # 파티션정보 저장소 생성
        self.partitions = {}  # 파티션별 스크랩데이터 저장소
        self.error_pages = {}  # 파티션별 에러페이지 저장
        self.success_pages = {}  # 파티션별 성공페이지 저장
        self.status = {}  # 파티션별 진행상태 저장
        self.successes = {}  # 파티션별 성공건수 저장
        self.processeds = {}  # 파티션별 처리건수 저장
        self.errors = {}  # 파티션별 에러건수 저장
        self.run_flags = {}  # 파티션별 실행 여부 플래그
        self.stop_flags = {} # 파티션별 중단 여부 플래그
        self.zip_flag = 0  # 파티션 병합 여부 플래그
        self.drivers = {} # 파티션별 브라우저 드라이버 저장
        self.htmls = {} # 파티션별 html 문서 저장
        self.soups = {} # 파티션별 BeautifulSoup 객체 저장
        self.processes = {} # 각 파티션의 프로세스 저장

        # 파티션저장소별 초기화
        for i in range(len(partition_sp) - 1):
            # 파티션별 키 생성 (키값에 파티션 페이지범위 포함)
            partition_key = (partition_sp[i] + 1, partition_sp[i + 1])
            self.open(partition_key) # 브라우저 오픈
            self.partitions[partition_key] = pd.DataFrame()
            self.error_pages[partition_key] = []
            self.success_pages[partition_key] = []
            self.status[partition_key] = "준비완료"
            self.successes[partition_key] = 0
            self.processeds[partition_key] = 0
            self.errors[partition_key] = 0
            self.processes[partition_key] = None
            self.run_flags[partition_key] = False
            self.stop_flags[partition_key] = True

    def start(self):

        if self.verbose == True: print("{} 개 프로세스로 작동합니다.".format(len(self.partitions.keys())))

        for partition_key in self.partitions:
            self.status[partition_key] = "진행중"
            self.processes[partition_key] = threading.Thread(target=self.crawl, args=(partition_key,))
            self.run_flags[partition_key] = True
            self.stop_flags[partition_key] = False

        for process in self.processes.values() :
            process.start()

        # for process in self.processes.values() :
        #     process.join()

    def restart(self, part_nm=None):

        keys = list(self.partitions.keys())
        if part_nm != None :
            if part_nm > len(keys) : print("{}번 프로세스는 없습니다."); return;
            partition_key = keys[part_nm + 1]
            self.run_flags[partition_key] = True
            self.status[partition_key] = "진행중"
            print("{} 프로세스 재시작".format(partition_key))

        else :
            for partition_key in keys :
                self.run_flags[partition_key] = True
                self.status[partition_key] = "진행중"
                print("{} 프로세스 재시작".format(partition_key))

    def pause(self, part_nm=None):

        keys = list(self.partitions.keys())
        if part_nm != None :
            if part_nm > len(keys) : print("{}번 프로세스는 없습니다."); return;
            partition_key = keys[part_nm + 1]
            self.run_flags[partition_key] = False
            self.status[partition_key] = "일시정지"
            print("{} 프로세스 일시정지".format(partition_key))

        else :
            for partition_key in keys :
                self.run_flags[partition_key] = False
                self.status[partition_key] = "일시정지"
                print("{} 프로세스 일시정지".format(partition_key))

    def stop(self, part_nm=None):

        keys = list(self.partitions.keys())
        if part_nm != None:
            if part_nm > len(keys): print("{}번 프로세스는 없습니다."); return;
            partition_key = keys[part_nm + 1]
            self.stop_flags[partition_key] = True
            self.status[partition_key] = "중단"
            print("{} 프로세스 중단".format(partition_key))

        else:
            for partition_key in keys:
                self.stop_flags[partition_key] = True
                self.status[partition_key] = "중단"
                print("{} 프로세스 중단".format(partition_key))
        time.sleep(2)
        self.close()

    def set_verbose(self, verbose):

        self.verbose = verbose

    def open(self, partition_key):

        self.drivers[partition_key] = self.set_driver(self.url)
        self.htmls[partition_key] = self.set_html(partition_key)
        self.soups[partition_key] = self.set_soup(partition_key)
        print("{} 페이지 브라우저를 오픈했습니다.".format(partition_key))

    def clear(self):

        import shutil
        try :
            shutil.rmtree("tmpdata/{}".format(self.page_type))
            print("데이터 삭제")
        except FileNotFoundError as e :
            print("기록이 없습니다.")

    def backup(self):

        import shutil
        from datetime import datetime
        timestamp = datetime.strftime(datetime.now(), "%m%d_%H%M")
        tmpdir = os.path.join(os.path.abspath(os.path.curdir), "tmpdata")
        backupdir = os.path.join(os.path.abspath(os.path.curdir), "backup")
        dstdir = os.path.join(backupdir, timestamp)
        if not os.path.isdir(backupdir):
            os.makedirs(backupdir)
        try :
            shutil.move(tmpdir, dstdir)
            print("{} 로 데이터를 백업했습니다.".format(
                os.path.join(dstdir, self.page_type)))
        except :
            pass

    def refresh(self, partition_key):
        for i in range(self.n_jobs) :
            self.htmls[partition_key] = self.set_html(partition_key)
            self.soups[partition_key] = self.set_soup(partition_key)

    def picker(self, partition_key, parant_tag, child_tag=None):
        '''
        웹페이지에서 검색대상 정보가 있는 태그를 설정하고 웹페이지 전체 데이터를 가져오는 함수
        :param parant_tag: 상위 태그 설정 인수
        :param child_tag: 하위 태그 설정 인수 (Default : None)
        :return: list타입의 list타입 변수
        '''
        tags = self.soups[partition_key].select(parant_tag)

        results = []
        for tag in tags :
            if child_tag != None :
                tag = tag.select(child_tag)
                tag = [data.text.strip() for data in tag]

            if tag == [] :
                continue
            results.append(tag)
        return results

    def fetch(self, partition_key,  keyword):
        '''
        추상화 함수 : 단일 레코드 크롤링 함수
        :param keyword: 검색어
        :return: 없음
        '''
        pass

    def insert(self, input_data, col):

        pass

    def takeout(self):
        '''
        크롤링한 데이터셋을 리턴하는 함수
        :return: data ( 타입 : 데이터프레임 or 딕셔너리(데이터프레임) )
        '''
        if self.n_jobs == 1:
            return self.partitions.pop()
        else:
            if self.zip_flag == 0:
                return self.partitions
            else:
                return self.data

    def save(self):

        self.data = pd.DataFrame()
        for partition in self.partitions.values():
            self.data = self.data.append(partition)
        self.data = self.data.reset_index(drop=True)
        print("데이터 병합")
        self.record()
        print("스크랩 로그기록")
        self.log()
        self.zip_flag = 1

    def monitor(self, second=2):

        self.set_verbose(False)
        while True:
            try:
                self.summary()
                clear_output(wait=True)
                time.sleep(second)

            except KeyboardInterrupt:
                break;
        self.set_verbose(True)
        print("모니터링 종료")

    def summary(self):

        print("-" * 108)
        for partition_key in self.partitions:
            line = "{:>15} 스크랩프로세스 | {:>5}% {} | 총 {:>6}건 | 성공 {:>6}건 | 실패 {:>6}건".format(
                str(partition_key),
                ("%.1f" % (self.processeds[partition_key] / (partition_key[1] - partition_key[0] + 1) * 100)),
                self.status[partition_key],
                partition_key[1] - partition_key[0] + 1,
                self.successes[partition_key],
                self.errors[partition_key],
            )
            print("|{:>82}     |".format(line))
        print("-" * 108)

        total_processeds = 0
        for i in self.processeds.values() : total_processeds += i
        total_successes = 0
        for i in self.successes.values(): total_successes += i
        total_errors = 0
        for i in self.errors.values(): total_errors += i
        total_status = "준비완료"
        for status in self.status.values() :
            if "진행중" in status :  total_status = "진행중"
        cnt = 0
        for status in self.status.values() :
            if "종료" in status : cnt +=1
        if cnt == len(self.status.values()) :
            total_status = "종료"
        percentage = (total_processeds / (self.end_page - self.start_page + 1)) * 100
        line = "{:>12} 스크랩프로세스 | {:>5}% {} | 총 {:>6}건 | 성공 {:>6}건 | 실패 {:>6}건".format(
            "전체",
            "%.1f" % percentage,
            total_status,
            self.end_page - self.start_page + 1,
            total_successes,
            total_errors,
        )
        print("|{:>80}     |".format(line))
        print("-" * 108)


    def record(self):

        filename = "total_{}_{}_{}".format(self.page_type, self.start_page, self.end_page)

        try:
            if not (os.path.isdir(os.path.join("tmpdata", self.page_type))):
                os.makedirs(os.path.join("tmpdata", self.page_type))
            if not (os.path.isdir(os.path.join("tmpdata", self.page_type, "data"))):
                os.makedirs(os.path.join("tmpdata", self.page_type, "data"))

        except OSError as e:
            if e.errno != errno.EEXIST:
                print("디렉토리 생성 실패.")
                raise


        try :
            with open("tmpdata/{}/data/{}.pkl".format(self.page_type, filename), "rb") as f:
                dump_data = pickle.load(f)
        except:
            dump_data = pd.DataFrame()
        dump_data = dump_data.append(self.data).reset_index(drop=True)

        with open("tmpdata/{}/data/{}.pkl".format(self.page_type, filename), "wb") as f:
            pickle.dump(dump_data, f)

        #기존 데이터와 병합
        try :
            file_data = pd.read_csv("tmpdata/{}/data/{}.csv".format(self.page_type, filename), encoding="utf8", index_col=False)
        except FileNotFoundError :
            file_data = pd.DataFrame()
        file_data = file_data.append(self.data).reset_index(drop=True)
        file_data.to_csv("tmpdata/{}/data/{}.csv".format(self.page_type, filename), encoding="utf8", index=False)

        print("{} 로 데이터를 저장했습니다.".format(os.path.join(os.path.abspath(os.path.curdir),"tmpdata",self.page_type, "data", filename + ".csv")))

    def load(self, filename):

        import pickle
        try :
            with open("tmpdata/{}/log/{}.pkl".format(self.page_type, filename), "rb") as f:
                data = pickle.load(f)
                return data
        except :
            return []

    def crawl(self, partition_key):

        pass

    def scrap(self, partition_key):

        pass

    def set_page(self, partition_key, page_nm):

        pass

    def _check(self, attr) :
        '''
        클래스 속성이 존재하는지 검사하는 함수(클래스 내부사용)
        :param attr: 속성 변수
        :return: 없음
        '''
        try:
            getattr(self, attr)
        except AttributeError:
            raise RuntimeError("FAILED : {} 를 확인해주세요.".format(attr))

    def set_soup(self, partition_key):
        '''
        BeautifulSoup 객체를 생성하는 Setter 함수
        :param url: url 문자열 값 입력 받는 인수
        :param browser: 헤드리스 브라우저 지정(Default : Chrome) #PhantomJs 사용가능
        :return: 없음
        '''
        return BeautifulSoup(self.htmls[partition_key], 'html.parser')

    def set_html(self, partition_key):
        '''
        문자열 타입 html 문서를 저장하는 Setter 함수
        :param url:
        :param browser:
        :return: 없음
        '''
        return self.drivers[partition_key].page_source

    def set_driver(self, url):
        '''
        selenium 패키지의 browser driver 모듈을 세팅하는 함수
        :param url: 문자열타입 url 주소를 입력받는 인수
        :param browser: 브라우저를 지정하는 인수 (Default : Chrome) # PhantomJS 도가능
        :return: 없음
        '''
        driver = None
        option = Options()
        option.add_argument('headless')
        option.add_argument('window-size=1920x1080')
        option.add_argument("disable-gpu")
        # Headless숨기기1
        option.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
        option.add_argument("lang=ko_KR")


        cur_dir = os.path.abspath(os.path.dirname(__file__))
        browser_dir = os.path.join(cur_dir, "browser")

        if self.browser == "Chrome":
            browser_file = browser_dir + "/chromedriver.exe"
            if self.headless == True :
                driver = webdriver.Chrome(browser_file, chrome_options=option)
            else :
                driver = webdriver.Chrome(browser_file)
            driver.get('about:blank')
            driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5]}})")
            driver.execute_script("const getParameter = WebGLRenderingContext.getParameter;WebGLRenderingContext.prototype.getParameter = function(parameter) {if (parameter === 37445) {return 'NVIDIA Corporation'} if (parameter === 37446) {return 'NVIDIA GeForce GTX 980 Ti OpenGL Engine';}return getParameter(parameter);};")

        else:
            browser_file = browser_dir + "/PhantomJS.exe"
            driver = webdriver.PhantomJS(browser_file)

        driver.execute_script("Object.defineProperty(navigator, 'languages', {get: function() {return ['ko-KR', 'ko']}})")
        driver.implicitly_wait(3)
        driver.get(url)
        return driver

    def get_text(self, partition_key):
        '''
        인스턴스의 html 변수의 텍스트 정보를 얻어오는 함수
        :return: 문자열 타입 text
        '''
        text = ""
        p = re.compile(r'(<.{1,5}/?>)(?P<content>[^<\n]+)(</.{1,5}>)', re.M)
        m = p.finditer(self.htmls[partition_key])
        lines = [line.group("content").strip() for line in m]
        for line in lines :
            text = text + "\n" + line
        return text

    def get_tags(self, partition_key):
        '''
        인스턴스의 html 변수의 사용된 tag 문자열 리스트를 리턴하는 함수
        :return: 문자열들의 list 타입
        '''
        alltags = self.soups[partition_key].find_all(True)
        alltags = [tag.name for tag in alltags]
        alltags = list(set(alltags))
        return alltags

    def get_attrs(self, partition_key):
        '''
        인스턴스의 html변수가 담고 있는 문서의 속성명을 문자열 리스트로 반환하는 함수
        :return: 문자열 list 타입
        '''
        tags = self.soups[partition_key].find_all(True)
        attrs_list = [[attr for attr in tag.attrs.keys()] for tag in tags]
        attrs = []
        for attr in attrs_list:
            attrs.extend(attr)
        attrs = list(set(attrs))
        return attrs

    def log(self):

        try:
            if not (os.path.isdir(os.path.join("tmpdata", self.page_type))):
                os.makedirs(os.path.join("tmpdata", self.page_type))
            if not (os.path.isdir(os.path.join("tmpdata", self.page_type, "log"))):
                os.makedirs(os.path.join("tmpdata", self.page_type, "log"))

        except OSError as e:
            if e.errno != errno.EEXIST:
                print("디렉토리 생성 실패.")
                raise

        #에러페이지 기록
        error_page_list = []
        for partition in self.error_pages.values() :
            error_page_list.extend(partition)
        pd.DataFrame(error_page_list).to_csv("tmpdata/{}/log/{}_pages.csv".format(self.page_type, "error"), encoding="utf8")
        with open("tmpdata/{}/log/{}_pages.pkl".format(self.page_type, "error"), "wb") as f:
            pickle.dump(error_page_list, f)
        print("{} 로 데이터를 저장했습니다.".format(
            os.path.join(os.path.abspath(os.path.curdir), "tmpdata", self.page_type, "log", "error_pages.csv")))
        #성공페이지 기록
        success_page_list = []
        for partition in self.success_pages.values():
            success_page_list.extend(partition)
        pd.DataFrame(success_page_list).to_csv("tmpdata/{}/log/{}_pages.csv".format(self.page_type, "success"), encoding="utf8")
        with open("tmpdata/{}/log/{}_pages.pkl".format(self.page_type, "success"), "wb") as f:
            pickle.dump(success_page_list, f)
        print("{} 로 데이터를 저장했습니다.".format(
            os.path.join(os.path.abspath(os.path.curdir), "tmpdata", self.page_type, "log", "success_pages.csv")))

    def __del__(self) :

        self.close()
        print("크롤러 종료")

class EPLCrawler(BigwingCrawler):

    def __init__(self, url='about:blank', page_range=None, page_type="Lineup", browser='Chrome', headless=True, n_jobs=1, verbose=True):

        super().__init__(url, page_range, page_type, browser, headless, n_jobs, verbose)

        if page_type=="Lineup" or  page_type=="Matchs" :

            self.url = "https://www.premierleague.com/match/"

        else : pass;
        time.sleep(2)

    def crawl(self, partition_key):
        #페이지 커서 설정
        cur_page = first_page = partition_key[0]; last_page = partition_key[1]
        error_flag = False
        #데이터셋 타입 결정
        if self.page_type == "Lineup" :  dataset = pd.DataFrame()
        elif self.page_type == "Matchs" : dataset = pd.DataFrame()
        else : pass

        #데이터 스크랩 프로세스
        while cur_page < (last_page + 1) :

            if cur_page in self.success_page_list : #이미 크롤링이 성공한 페이지는 넘어가기
                if cur_page < (last_page + 1) :
                    self.success_pages[partition_key].extend([cur_page])
                    self.processeds[partition_key] +=1
                    self.successes[partition_key] +=1
                    cur_page += 1
                    continue

                else : break;

            self.status[partition_key] = "{}번 스크랩중".format(cur_page)

            while self.run_flags[partition_key] == False :  time.sleep(0.5) # 일시정지
            if self.stop_flags[partition_key] == True : break; # 중단

            try:
                self.set_page(partition_key, cur_page)
                # 스크랩
                if self.page_type == "Lineup":  # 라인업 페이지 크롤러
                    data = self.scrap_lineup(partition_key)
                elif self.page_type == "Matchs":  # 매치 페이지 크롤러
                    data = self.scrap_matchstats(partition_key)
                else: pass;

                data.insert(0, "Match_ID", cur_page) #페이지 넘버 스탬프
                # 매치정보가 많이 부족할때 에러 체크
                if data.shape[1] < 10 :
                    error_flag = True
                    if self.verbose == True: print("{}번 스크랩실패.".format(cur_page))
                else:
                    error_flag = False
                    if self.verbose == True: print("{}번 스크랩성공.".format(cur_page))
                    # 기존기록에 추가
                    dataset = dataset.append(data).fillna("")

                self.partitions[partition_key] = dataset.reset_index(drop=True)

            except Exception as e:

                if self.verbose == True : print("{} : {}번 스크랩실패".format(e, cur_page))
                error_flag = True
                
            #현재 페이지 스크랩결과 기록
            self.processeds[partition_key] += 1
            if error_flag == False  :     
                self.successes[partition_key] += 1  # 성공건수 기록
                self.success_pages[partition_key].extend([cur_page])  # 성공페이지 기록
                self.success_page_list.extend([cur_page])
            else                    :     
                self.errors[partition_key] += 1  # 실패건수 기록
                self.error_pages[partition_key].extend([cur_page])  # 에러페이지 기록
                self.error_page_list.extend([cur_page])

            cur_page += 1

        #스크랩 상태 저장 & 리포트
        if self.verbose == True: print("({}, {}) 프로세스 스크랩완료".format(first_page, last_page))
        self.status[partition_key] = "완료" if self.stop_flags[partition_key] == True else "종료"

    def close(self):

        for partition_key in self.partitions:
            try :
                self.drivers[partition_key].close()
            except : pass
            try :
                self.drivers[partition_key].quit()
            except : pass
            print("{} 브라우저를 종료했습니다.".format(partition_key))

    def scrap_matchstats(self, partition_key):

        # 매치 기본 정보
        matchInfo = self.drivers[partition_key].find_element_by_class_name("matchInfo").text.split("\n")
        # 매치 클럽 이름
        home_nm = self.drivers[partition_key].find_element_by_xpath(
            "//*[@id='mainContent']/div/section/div[2]/section/div[3]/div/div/div[1]/div[1]/a[2]/span[1]").text
        away_nm = self.drivers[partition_key].find_element_by_xpath(
            "//*[@id='mainContent']/div/section/div[2]/section/div[3]/div/div/div[1]/div[3]/a[2]/span[1]").text
        # 경기 스코어
        score = self.drivers[partition_key].find_element_by_xpath(
            "//*[@id='mainContent']/div/section/div[2]/section/div[3]/div/div/div[1]/div[2]/div").text
        dataset = self.picker(partition_key, "tr", "td")
        cols = ["matchinfo_"+str(i+1) for i in range(len(matchInfo))] + ["home_team", "score", "away_team"] + ["home_" + data[1] for data in dataset] + ["away_" + data[1] for data in dataset]
        vals = matchInfo + [home_nm, score, away_nm] + [data[0] for data in dataset] + [data[2] for data in dataset]
        matchstats = pd.DataFrame(columns=cols)
        matchstats.loc[0] = vals
        return matchstats

    def scrap_lineup(self, partition_key):

        lineup = pd.DataFrame(
            columns=["Team", "Number", "Name", "Goal", "Sub_On_Off", "Sub_Time", "Card", "Playing", "Position",
                     "Nationality"])

        for team in range(2):
            # 포지션리스트
            position_list = [position.text for position in self.soups[partition_key].find_all("div", "matchLineupTeamContainer")[team].select("h3")]
            groups = self.soups[partition_key].find_all("div", "matchLineupTeamContainer")[team].select("ul")
            # 각 그룹들
            for group_idx, group in enumerate(groups):
                players = groups[group_idx].find_all("li", "player")
                # 각 선수들
                for player in players:
                    player_info = []
                    team_nm = self.soups[partition_key].select("header.squadHeader > div.position")[team].find(text=True).strip()
                    player_info.append(team_nm)  # 팀이름
                    number = player.find("div", "number").get_text().replace("Shirt number ", "");
                    player_info.append(number)  # 선수 넘버
                    info_tag = player.select("div.info")
                    for tag in info_tag:
                        nametag = tag.select(".name")[0]
                        name = nametag.find(text=True).strip();
                        player_info.append(name)  # 선수이름
                        try:  # 골수
                            p = re.compile(r'icn ball')
                            m = p.findall(str(nametag))
                            player_info.append(len(m))
                        except:
                            player_info.append(0)
                        try:  # 경기 인아웃
                            p = re.compile(r'sub-on|sub-off')
                            m = p.search(str(nametag))
                            if m.group(0) == "sub-on":
                                player_info.append("On")
                            elif m.group(0) == "sub-off":
                                player_info.append("Off")
                        except:
                            player_info.append("")
                        try:  # 교체 시간
                            player_info.append(nametag.select("span.sub")[0].text)
                        except:
                            player_info.append("")
                        try:  # 카드 여부
                            p = re.compile(r'yellow|red')
                            m = p.search(str(nametag))
                            if m.group(0) == "yellow":
                                player_info.append("Yellow")
                            elif m.group(0) == "red":
                                player_info.append("Red")
                        except:
                            player_info.append("")
                        try:  # 주전/후보 여부
                            player_info.append("starter" if position_list[group_idx] != "Substitutes" or group_idx >= 4 else "substitutes")
                        except:
                            player_info.append("substitutes")
                        try:  # 포지션
                            player_info.append(tag.select(".position")[0].text.strip())
                        except:
                            player_info.append(position_list[group_idx])
                        try:  # 국가
                            player_info.append(tag.select(".nationality")[0].text.strip())
                        except:
                            player_info.append("")
                    lineup.loc[lineup.shape[0]] = player_info

        # 경기정보
        try:
            matchinfo = [""] * 4
            matchinfo_tmp = [info.text.replace("Att: ", "") for info in self.soups[partition_key].select("div.matchInfo > div")]
            for idx, info in enumerate(matchinfo_tmp):
                matchinfo[idx] = info
        except :
            matchinfo = [""] * 4

        lineup.insert(0, "Match_Date", matchinfo[0])
        lineup.insert(1, "Referee", matchinfo[1])
        lineup.insert(2, "Stadium", matchinfo[2])
        lineup.insert(3, "Attendence", matchinfo[3])
        try:
            score = self.soups[partition_key].select("div.score")[0].text
        except:
            score = ""
        lineup.insert(4, "Score", score)

        return lineup

    def set_page(self, partition_key, page_nm) :

        dst_url = self.url + str(page_nm)
        self.drivers[partition_key].get(dst_url)
        try:
            if not (os.path.isdir(os.path.join("tmpdata", self.page_type))):
                os.makedirs(os.path.join("tmpdata", self.page_type))

        except OSError as e:
            if e.errno != errno.EEXIST:
                print("디렉토리 생성 실패.")
                raise

        time.sleep(0.3)

        if self.page_type == "Lineup" :
            if self.drivers[partition_key].find_element_by_class_name("matchCentreSquadLabelContainer").text.strip() == 'Line-ups' :
                self.drivers[partition_key].find_element_by_class_name("matchCentreSquadLabelContainer").click()
            else : raise NameError('NoLineups')

        elif self.page_type == "Matchs" :
            self.drivers[partition_key].find_element_by_xpath(
                "//*[@id='mainContent']/div/section/div[2]/div[2]/div[1]/div/div/ul/li[3]").click()

        time.sleep(0.2)
        self.refresh(partition_key)
