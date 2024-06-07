from time import sleep
from urllib.request import urlopen
from django.conf import settings
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

from app.utils.logger import Logger
from config.properties import (
    URL_NETFLIX_LOGIN,
    URL_NETFLIX_CONTENT
)


class BeautyfulSoupParser:
    def __init__(self):
        self._soup = None

    def set_beautyfulsoup(self, html):
        parser = "html.parser"
        self._soup = BeautifulSoup(html, parser)

    def soup_element(self, tag, classname=None, attrs=None):
        result = None
        if classname is not None and attrs is not None:
            result = self._soup.find(tag, class_=classname, attrs=attrs)
        elif classname is not None:
            result = self._soup.find(tag, class_=classname)
        elif attrs is not None:
            result = self._soup.find(tag, attrs=attrs)    
        return result
    
    def soup_elements(self, tag, classname=None, attrs=None):
        result = []
        if classname is not None and attrs is not None:
            result = self._soup.find_all(tag, class_=classname, attrs=attrs)
        elif classname is not None:
            result = self._soup.find_all(tag, class_=classname)
        elif attrs is not None:
            result = self._soup.find_all(tag, attrs=attrs)
        return result

    def soup_close(self):
        self._soup.decompose()


class SeleniumParser:
    def __init__(self):
        self._selenium = None

    def set_selenium(self, url, driver="chrome"):
        options = Options()
        options.add_experimental_option("detach", True)
        # navigator.webdriver = false 로 만들어주는 옵션.
        # options.add_argument("--disable-blink-features=AutomationControlled")
        if driver == "chrome":
            try:
                self._selenium = webdriver.Chrome(options=options)
                self._selenium.get(url)
                self.wait(2)
                Logger.info_log(self.__class__.__name__, "driver is ready")
                return True
            except Exception as e:
                Logger.error_log(self.__class__.__name__, str(e))
                return False
        else:
            Logger.error_log(self.__class__.__name__, "Not supported driver")
            return False
    
    def selenium_element(self, type=None, value=None, target=None):
        Logger.info_log(self.__class__.__name__, "selenium_element")
        result = None
        if type not in ["class", "name", "id", "tag"]:
            Logger.error_log(self.__class__.__name__, "Not supported type")
            return result
        try:
            if target is None:
                target = self._selenium
            if type == "class":
                result = target.find_element(by=By.CLASS_NAME, value=value)
            elif type == "name":
                result = target.find_element(by=By.NAME, value=value)
            elif type == "id":
                result = target.find_element(by=By.ID, value=value)
            elif type == "tag":
                result = target.find_element(by=By.TAG_NAME, value=value)
            else:
                print("Not supported type")
        except Exception as e:
            Logger.error_log(self.__class__.__name__, str(e))
        return result
        
    def selenium_elements(self, type=None, value=None, target=None):
        Logger.info_log(self.__class__.__name__, "selenium_elements")
        result = None
        try:
            if target == None:
                target = self._selenium
            if type == "class":
                result = target.find_elements(by=By.CLASS_NAME, value=value)
            elif type == "name":
                result = target.find_elements(by=By.NAME, value=value)
            elif type == "id":
                result = target.find_elements(by=By.ID, value=value)
            elif type == "tag":
                result = target.find_elements(by=By.TAG_NAME, value=value)
            else:
                Logger.error_log(self.__class__.__name__, "Not supported type")
        except Exception as e:
            Logger.error_log(self.__class__.__name__, str(e))
        return result

    def selenium_attribute(self, target, attr):
        Logger.info_log(self.__class__.__name__, "selenium_attribute")
        result = None
        if attr is not None:
            try:
                result = target.get_attribute(attr)
            except Exception as e:
                Logger.error_log(self.__class__.__name__, str(e))
        return result
    
    def selenium_click(self, target):
        Logger.info_log(self.__class__.__name__, "selenium_click")
        if target is not None:
            try:
                target.click()
                self.selenium_wait(2)
                return True
            except Exception as e:
                Logger.error_log(self.__class__.__name__, str(e))
                return False
        else:
            Logger.error_log(self.__class__.__name__, "Target is None")
            return False
    
    def selenium_wait(self, sec):
        Logger.info_log(self.__class__.__name__, "selenium_wait")
        sleep(sec)

    def selenium_scroll_move(self, target):
        info_log(self.__class__.__name__, "selenium_scroll_move")
        target.location_once_scrolled_into_view

    def selenium_scroll_down(self):
        info_log(self.__class__.__name__, "selenium_scroll_down")
        if self._selenium is not None:
            try:
                # PAGE_DOWN 키를 이용하여 스크롤 다운
                body = self.selenium_element(type="tag", value="body")
                body.send_keys(Keys.PAGE_DOWN)
                # 웨이팅 (2s)
                self.selenium_wait(2)
                return True
            except Exception as e:
                info_log(self.__class__.__name__, str(e))
                return False
        else:
            return False

    def selenium_scroll_up(self):
        info_log(self.__class__.__name__, "selenium_scroll_up")
        if self._selenium is not None:
            try:
                # PAGE_DOWN 키를 이용하여 스크롤 다운
                body = self.selenium_element(type="tag", value="body")
                body.send_keys(Keys.PAGE_UP)
                # 웨이팅 (2s)
                self.selenium_wait(2)
                return True
            except Exception as e:
                info_log(self.__class__.__name__, str(e))
                return False
        else:
            return False

    def selenium_close(self):
        if self._selenium is not None:
            info_log(self.__class__.__name__, "Selenium driver is closed")
            self._selenium.quit()


class NetflixParser(BeautyfulSoupParser, SeleniumParser):

    def login_netflix(self, id, pw):
        info_log(self.__class__.__name__, "Try to login netflix. id={}".format(id))
        try:
            netflix_id = self.selenium_element(type="name", value="userLoginId")
            netflix_pw = self.selenium_element(type="name", value="password")
            netflix_id.send_keys(id)
            netflix_pw.send_keys(pw)
            netflix_pw.send_keys(Keys.RETURN)
            # 로그인 후 페이지 전환 대기 (3s)
            self.selenium_wait(3)
            info_log(self.__class__.__name__, "Netflix login success")
            return True
        except Exception as e:
            error_log(self.__class__.__name__, "Failed netflix login. {}".format(e))
            return False

    def get_content_netflix(self, id):
        info_log(self.__class__.__name__, "Try to import content. id={}".format(id))
        url = URL_NETFLIX_CONTENT + "/" + id
        try:
            with urlopen(url) as response:
                html = response.read()
            # BeautySoup을 이용하여 데이터 파싱
            content = self.parse_content_netflix(html)
            info_log(self.__class__.__name__, "Content import success. content={}".format(content))
            return content
        except Exception as e:
            error_log(self.__class__.__name__, "Failed to import content. {}".format(e))
            return None
            
    def get_contents(self):
        info_log(self.__class__.__name__, "Try to get most watched contents")
        try:
            # 넷플릭스 로그인
            self.set_selenium(URL_NETFLIX_LOGIN)
            self.selenium_wait(2)
            self.login_netflix(getattr(settings, "NETFLIX_ID"), getattr(settings, "NETFLIX_PW"))
            self.selenium_wait(2)
            # 컨텐츠와 랭크 정보를 담을 리스트 초기화
            ranks = []
            contents = []
            # 컨텐츠 파싱작업
            content_rows = self.selenium_elements(type="class", value="lolomoRow")
            for content_row in content_rows:
                # 컨텐츠가 화면에 보이도록 스크롤 이동
                self.selenium_scroll_move(target=content_row)
                self.selenium_wait(2)
                # 컨텐츠의 더보기 요소를 클릭하여 추가 요소가 렌더링 되도록 함
                handle_next = self.selenium_element(type="class", value="handleNext", target=content_row)
                self.selenium_click(target=handle_next)
                self.selenium_wait(2)
                # 컨텐츠 타이틀
                content_row_title = self.selenium_element(type="class", value="rowHeader", target=content_row).text
                # content_row 에 담긴 데이터 리스트
                content_row_items = self.selenium_elements(type="class", value="slider-item", target=content_row)
                # content_row type
                content_row_type = self.selenium_attribute(target=content_row, attr="data-list-context")
                # 컨텐츠 갯수만큼 반복
                for item in content_row_items:
                    # 필수 정보 파싱
                    content = dict()
                    link = self.selenium_element(type="tag", value="a", target=item)
                    link = self.selenium_attribute(target=link, attr="href")
                    content['platform_id'] = link.split("?")[0].split("/watch/")[1]
                    content['watch'] = [{"type": "10", "url": link}]
                    # mostWatched 일 경우 rank 정보 수집
                    if content_row_type == "mostWatched":
                        rank_dict = dict()
                        if content_row_title == "오늘 대한민국의 TOP 10 시리즈":
                            rank_dict['type'] = "series"
                        elif content_row_title == "오늘 대한민국의 TOP 10 영화":
                            rank_dict['type'] = "movies"
                        rank = self.selenium_element(type="tag", value="svg", target=item)
                        rank = self.selenium_attribute(target=rank, attr="id").split("-")[1]
                        rank_dict['rank'] = int(rank)
                        rank_dict['platform_code'] = "10"
                        rank_dict['platform_id'] = str(content['platform_id'])
                        rank_dict['thumbnail'] = self.selenium_attribute(
                            target=self.selenium_element(type="tag", value="img", target=item),
                            attr="src"
                        )
                        # 중복데이터 방지
                        if rank_dict not in ranks:
                            ranks.append(rank_dict)
                        # 포스터 아까우니까 컨텐츠에도 일단 담음
                        content['thumbnail'] = {"type": "10", "url": rank_dict['thumbnail'], "extension": "", "size": 0}
                    # 중복데이터 방지
                    if content not in contents:
                        contents.append(content)
            # rank 순으로 정렬
            ranks = sorted(ranks, key=lambda k: (k['type'], k['rank']))
            # Write Log
            info_log(self.__class__.__name__, "Most watched contents parsing success")
            # 파싱한 데이터 리턴
            return contents, ranks
        except Exception as e:
            # Write Log
            error_log(self.__class__.__name__, "Failed to most watched contents parsing. {}".format(e))
            # 에러 발생시 None
            return None, None
    
    def parse_content(self, html):
        info_log(self.__class__.__name__, "Try to parse netflix content")
        try:
            self.set_beautyfulsoup(html)        
            schema = self.soup_element(tag="script", attrs={"type": "application/ld+json"})
            schema = schema.text.strip()
            schema_to_dict = eval(schema)

            content = dict()
            # type 추출
            content['type'] = "" 
            if schema_to_dict['@type'] == "Movie":
                content['type'] = "10"
            elif schema_to_dict['@type'] == "TVSeries":
                content['type'] = "11"
            content['title'] = schema_to_dict['name'] # title 추출
            content['synopsis'] = schema_to_dict['description'] # synopsis 추출
            content['platform_code'] = "10" # Netflix platform_code
            content['platform_id'] = schema_to_dict['url'].split("/")[-1] # platform_id 추출
            content['notice_age'] = schema_to_dict['contentRating'] # 연령고지 추출
            # Thumbnail 이미지 추출
            content['thumbnail'] = [
                {"type": "11", "url": schema_to_dict['image'], "extension": "", "size": 0}
            ]
            # watch url 추출
            content['watch'] = [
                {"type": "10", "url": schema_to_dict['url']}  
            ]
            # 장르 추출
            content['genre'] = []
            genres = self.soup_elements(tag="a", classname="item-genres")
            for genre in genres:
                content['genre'].append({"name": genre.text.strip()})
            # 출연진 추출
            content['actor'] = []
            actor_count = 0
            for actor in schema_to_dict['actors']:
                type = "10"
                if actor_count > 1:
                    type = "11"
                content['actor'].append({"type": type, "name": actor['name'], "role": "", "picture": "", "profile": ""})
                actor_count += 1
            # 제작진 초기화
            content['staff'] = []
            # 감독 추출
            for director in schema_to_dict['director']:
                content['staff'].append({"type": "10", "name": director['name'], "picture": "", "profile": ""})
            # 제작진 추출
            for creator in schema_to_dict['creator']:
                content['staff'].append({"type": "11", "name": creator['name'], "picture": "", "profile": ""})
            # 파싱 범위 축소
            self._soup = self.soup_element(tag="div", classname="hero-container")
            # release 추출
            content['release'] = self.soup_element(tag="span", classname="item-year")
            if content['release'] is not None:
                content['release'] = content['release'].text.strip()
            # 상영시간 추출
            content['runtime'] = self.soup_element(tag="span", classname="item-runtime", attrs={"data-uia": "item-runtime"})
            if content['runtime'] is not None:
                content['runtime'] = content['runtime'].text.strip()
            
            info_log(self.__class__.__name__, "Netflix content parsing success")
            return content
        except Exception as e:
            error_log(self.__class__.__name__, "Failed to parse content. {}".format(e))
            return None
        finally:
            self.soup_close()

    def close(self):
        info_log(self.__class__.__name__, "Close NetflixParser")
        try:
            if self._selenium is not None:
                self.selenium_close()
            if self._soup is not None:
                self.soup_close()
        except Exception as e:
            error_log(self.__class__.__name__, str(e))
