import json
from abc import ABC, abstractmethod
from time import sleep

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.constraints import NETFLIX_LOGIN_URL, NETFLIX_CONTENT_URL, TVING_LOGIN_URL, TVING_CONTENT_URL
from config.settings import settings


class SeleniumParser:
    def __init__(self):
        self.driver = None

    def set_driver(self, url, driver="chrome"):
        options = Options()
        options.add_experimental_option("detach", True)
        # navigator.webdriver = false 로 만들어주는 옵션.
        # options.add_argument("--disable-blink-features=AutomationControlled")
        if driver == "chrome":
            try:
                self.driver = webdriver.Chrome(options=options)
                self.driver.get(url)
                return True
            except Exception as e:
                raise e
        else:
            return False

    def get_element(self, type=None, value=None, target=None):
        result = None
        if type not in ["class", "name", "id", "tag"]:
            return result
        try:
            if type == "class":
                result = target.find_element(by=By.CLASS_NAME, value=value)
            elif type == "name":
                result = target.find_element(by=By.NAME, value=value)
            elif type == "id":
                result = target.find_element(by=By.ID, value=value)
            elif type == "tag":
                result = target.find_element(by=By.TAG_NAME, value=value)
            return result
        except Exception as e:
            raise e

    def get_elements(self, type=None, value=None, target=None):
        result = None
        try:
            if type == "class":
                result = self.driver.find_elements(by=By.CLASS_NAME, value=value)
            elif type == "name":
                result = target.find_elements(by=By.NAME, value=value)
            elif type == "id":
                result = target.find_elements(by=By.ID, value=value)
            elif type == "tag":
                result = target.find_elements(by=By.TAG_NAME, value=value)
            return result
        except Exception as e:
            raise e

    def get_attribute(self, target, attr):
        result = None
        if attr is not None:
            try:
                result = target.get_attribute(attr)
            except Exception as e:
                raise e
        return result

    def click(self, target):
        if target is not None:
            try:
                target.click()
                self.wait(2)
                return True
            except Exception as e:
                raise e
        else:
            return False

    def wait(self, sec):
        sleep(sec)

    def scroll_move(self, target):
        target.location_once_scrolled_into_view

    def scroll_down(self):
        if self.driver is not None:
            try:
                # PAGE_DOWN 키를 이용하여 스크롤 다운
                body = self.get_element(type="tag", value="body")
                body.send_keys(Keys.PAGE_DOWN)
                # 웨이팅 (2s)
                self.wait(2)
                return True
            except Exception as e:
                raise e
        else:
            return False

    def scroll_up(self):
        if self.driver is not None:
            try:
                # PAGE_DOWN 키를 이용하여 스크롤 다운
                body = self.get_element(type="tag", value="body")
                body.send_keys(Keys.PAGE_UP)
                # 웨이팅 (2s)
                self.wait(2)
                return True
            except Exception as e:
                raise e
        else:
            return False

    def close(self):
        if self.driver is not None:
            self.driver.quit()


class BeautyfulSoupParser:
    def __init__(self):
        self.soup = None

    def set_parser(self, html):
        parser = "html.parser"
        self.soup = BeautifulSoup(html, parser)

    def get_element(self, tag, classname=None, attrs=None):
        result = None
        if classname is not None and attrs is not None:
            result = self.soup.find(tag, class_=classname, attrs=attrs)
        elif classname is not None:
            result = self.soup.find(tag, class_=classname)
        elif attrs is not None:
            result = self.soup.find(tag, attrs=attrs)
        return result

    def get_elements(self, tag, classname=None, attrs=None):
        result = []
        if classname is not None and attrs is not None:
            result = self.soup.find_all(tag, class_=classname, attrs=attrs)
        elif classname is not None:
            result = self.soup.find_all(tag, class_=classname)
        elif attrs is not None:
            result = self.soup.find_all(tag, attrs=attrs)
        return result

    def close(self):
        self.soup.decompose()


class OTTParser(ABC):
    def __init__(self, ott_type=None, ott_content_url=None):
        self.ott_type = ott_type
        self.ott_content_url = ott_content_url
    @abstractmethod
    def parse(self, content_id):
        pass


class NetflixParser(OTTParser):
    def __init__(self):
        super().__init__("10", NETFLIX_CONTENT_URL)

    def parse(self, content_id):
        selenium = None
        try:
            content = dict()
            response = requests.get(self.ott_content_url + content_id)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            schema = soup.find("script", attrs={"type": "application/ld+json"})
            schema_to_dict = eval(schema.text.strip())
            content['type'] = schema_to_dict['@type'] == "Movie" and "10" or "11"
            content['platform_code'] = self.ott_type
            content['platform_id'] = content_id
            content['title'] = schema_to_dict['name']
            content['synopsis'] = schema_to_dict['description']
            content['notice_age'] = schema_to_dict['contentRating']
            # 출시정보 추출
            release = soup.find("span", class_="item-year")
            if release is not None:
                content['release'] = release.text.strip()
            # 장르 추출
            content['genre'] = []
            genres = soup.find_all("a", class_="item-genres")
            for genre in genres:
                content['genre'].append({"name": genre.text.strip()})
            # 썸네일 추출
            content['thumbnail'] = [{
                "type": "11", "url": schema_to_dict['image'], "extension": "", "size": 0, "width": 0, "height": 0
            }]
            # 시청정보 추출
            content['watch'] = [{"type": "10", "url": schema_to_dict['url']}]
            # 출연진 추출
            content['actor'] = list()
            actor_count = 0
            for actor in schema_to_dict['actors']:
                actor_type = "10"
                if actor_count > 1:
                    actor_type = "11"
                content['actor'].append({
                    "type": actor_type, "name": actor['name'], "role": "", "picture": "", "profile": ""
                })
                actor_count += 1
            # 감독 추출
            content['staff'] = list()
            for director in schema_to_dict['director']:
                content['staff'].append({"type": "10", "name": director['name'], "picture": "", "profile": ""})
            # 제작진 추출
            for creator in schema_to_dict['creator']:
                content['staff'].append({"type": "11", "name": creator['name'], "picture": "", "profile": ""})
            # 상영시간 추출
            runtime = soup.find("span", class_="item-runtime")
            if runtime is not None:
                content['runtime'] = runtime.text.strip()
            soup.decompose()
            return content

        except Exception as e:
            raise e

    @classmethod
    def boxoffice(cls):
        driver = None
        ranks = list()
        videos = list()
        try:
            # selenium 설정
            selenium_options = Options()
            # options.add_experimental_option("detach", True) # 브라우저 종료 방지
            selenium_options.add_argument("--headless")  # 헤드리스 모드 설정
            selenium_options.add_argument("--no-sandbox")
            selenium_options.add_argument("--disable-dev-shm-usage")
            # WebDriver 설정
            driver = webdriver.Chrome(options=selenium_options)
            # Netflix 로그인 페이지 호출
            driver.get(NETFLIX_LOGIN_URL)
            sleep(2)
            # 넷플릭스 로그인
            driver.find_element(by=By.NAME, value="userLoginId").send_keys(settings.NETFLIX_ID)
            driver.find_element(by=By.NAME, value="password").send_keys(settings.NETFLIX_PW)
            driver.find_element(by=By.NAME, value="password").send_keys(Keys.RETURN)
            sleep(2)
            # body 태그가 로딩될때까지 대기
            body = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            # 스크롤 다운 & 업
            body.send_keys(Keys.PAGE_DOWN)
            sleep(2)
            body.send_keys(Keys.PAGE_UP)
            sleep(2)
            # 컨텐츠 목록 가져오기
            content_rows = driver.find_elements(by=By.CLASS_NAME, value="lolomoRow")
            for content_row in content_rows:
                # 해당 컨텐츠 ROW로 스크롤 이동
                driver.execute_script("arguments[0].scrollIntoView();", content_row)
                sleep(2)
                # NEXT 버튼 클릭해서 추가 컨텐츠 로드
                try:
                    element = WebDriverWait(content_row, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'span.handle.handleNext.active'))
                    )
                    element.click()
                    sleep(2)
                except Exception as e:
                    print(e)
                # handle_next_list = content_row.find_elements(by=By.CLASS_NAME, value="handleNext")
                # if len(handle_next_list) > 0:
                #     handle_next_list[0].click()
                #     sleep(2)
                # 컨텐츠 ROW 타이틀
                content_row_title = ""
                try:
                    content_row_title = content_row.find_element(by=By.CLASS_NAME, value="rowHeader").text
                except Exception as e:
                    print(e)
                # 컨텐츠 ROW 아이템
                content_row_items = content_row.find_elements(by=By.CLASS_NAME, value="slider-item")
                for item in content_row_items:
                    video = dict()
                    rank = dict()
                    try:
                        link = item.find_element(by=By.TAG_NAME, value="a").get_attribute("href")
                        video['platform_id'] = link.split("?")[0].split("/watch/")[1]
                        # mostWatched 컨텐츠 ROW 식별
                        if content_row_title in ["오늘 대한민국의 TOP 10 시리즈", "오늘 대한민국의 TOP 10 영화"]:
                            # mostWatched 컨텐츠는 랭킹데이터 저장
                            rank['type'] = "movie" if content_row_title == "오늘 대한민국의 TOP 10 영화" else "series"
                            rank['rank'] = int(item.find_element(by=By.TAG_NAME, value="svg").get_attribute("id").split("-")[1])
                            rank['platform_code'] = "10"
                            rank['platform_id'] = str(video['platform_id'])
                            if rank not in ranks:
                                ranks.append(rank)
                            # 랭킹 컨텐츠에 있는 이미지 추출
                            video['thumbnail'] = {
                                "type": "10",
                                "url": item.find_element(by=By.TAG_NAME, value="img").get_attribute("src"),
                                "extension": "",
                                "size": 0,
                                "width": 0,
                                "height": 0
                            }
                        # 컨텐츠 목록에 추가
                        if video not in videos:
                            videos.append(video)
                    except Exception as e:
                        print(e)
                        continue
            # 랭킹 데이터 재정렬
            ranks = sorted(ranks, key=lambda k: (k['type'], k['rank']))
            # 컨텐츠 리턴
            return ranks, videos
        except Exception as e:
            raise e
        finally:
            # Selenium 종료
            if driver is not None:
                driver.quit()


class TvingParser(OTTParser):
    def __init__(self):
        super().__init__("12", TVING_CONTENT_URL)

    def parse(self, content_id):
        selenium = None
        try:
            content = dict()
            # selenium 설정
            selenium_options = Options()
            # options.add_experimental_option("detach", True) # 브라우저 종료 방지
            selenium_options.add_argument("--headless")  # 헤드리스 모드 설정
            selenium_options.add_argument("--no-sandbox")
            selenium_options.add_argument("--disable-dev-shm-usage")
            # selenium webdriver 설정
            selenium = webdriver.Chrome(options=selenium_options)
            # 컨텐츠 URL 호출
            selenium.get(self.ott_content_url + content_id)
            # 페이지 로딩되는 동안 대기
            sleep(2)
            # 컨텐츠 스키마 가져오기
            schema = selenium.find_element(By.CSS_SELECTOR, 'head script[type="application/ld+json"]')
            schema_to_dict = json.loads(schema.get_attribute('innerHTML'))
            # 컨텐츠 정보 수집
            content['type'] = schema_to_dict['@type'] == "Movie" and "10" or "11"
            content['platform_code'] = self.ott_type
            content['platform_id'] = content_id
            content['title'] = ""
            content['release'] = schema_to_dict['startDate']
            content['notice_age'] = schema_to_dict['contentRating']
            # 런타임 수집
            content['runtime'] = ""
            tag_parent = selenium.find_element(By.CSS_SELECTOR, 'div.tag_detail')
            tag_elements = tag_parent.find_elements(By.CSS_SELECTOR, 'div.tag-blank')
            for tag_element in tag_elements:
                if tag_element.text.find("분") > -1 or tag_element.text.find("시즌") > -1:
                    content['runtime'] = tag_element.text
                    break
            # 시놉시스 수집
            # desc = selenium.find_element(By.CSS_SELECTOR, 'meta[name="description"]')
            # content['synopsis'] = desc.get_attribute('content')
            content['synopsis'] = schema_to_dict['description']
            # 장르 수집
            content['genre'] = [{"name": schema_to_dict['genre']}]
            # 배우 수집
            content['actor'] = []
            actor_count = 0
            for actor in schema_to_dict['actors']:
                actor_type = "10"
                if actor_count > 1:
                    actor_type = "11"
                content['actor'].append({
                    "type": actor_type, "name": actor['name'], "role": "", "picture": "", "profile": ""
                })
                actor_count += 1
            # 제작진 수집
            content['staff'] = []
            for creator in schema_to_dict['creator']:
                content['staff'].append({"type": "11", "name": creator['name'], "picture": "", "profile": ""})
            # 썸네일 수집
            content['thumbnail'] = []
            img_tags = selenium.find_elements(by=By.TAG_NAME, value='img')
            for img_tag in img_tags:
                if (
                    img_tag.get_attribute('src').find(content_id) > 0
                    and img_tag.get_attribute('src').find("image.tving.com") > -1
                ):
                    if img_tag.get_attribute('src').split("/")[-1] == "1280":
                        content['title'] = img_tag.get_attribute('alt')
                        content['thumbnail'].append({
                            "type": "11",
                            "url": img_tag.get_attribute('src'),
                            "extension": "",
                            "size": 0
                        })
                    elif img_tag.get_attribute('src').split("/")[-1] == "480":
                        content['thumbnail'].append({
                            "type": "10",
                            "url": img_tag.get_attribute('src'),
                            "extension": "",
                            "size": 0
                        })
                    else:
                        continue
            content['watch'] = [{"type": self.ott_type, "url": selenium.current_url}]
            # selenium 종료
            selenium.quit()
            return content
        except Exception as e:
            raise e
        finally:
            if selenium is not None:
                selenium.quit()

    @classmethod
    def boxoffice(cls):
        driver = None
        ranks = list()
        videos = list()
        try:
            # selenium 설정
            selenium_options = Options()
            selenium_options.add_experimental_option("detach", True)  # 브라우저 종료 방지
            # selenium_options.add_argument("--headless")  # 헤드리스 모드 설정
            selenium_options.add_argument("--no-sandbox")
            selenium_options.add_argument("--disable-dev-shm-usage")
            # WebDriver 설정
            driver = webdriver.Chrome(options=selenium_options)
            # Tving 로그인 페이지 호출
            driver.get(TVING_LOGIN_URL)
            sleep(2)
            # Tving 로그인
            driver.find_element(value="a").send_keys(settings.TVING_ID)
            driver.find_element(value="b").send_keys(settings.TVING_PW)
            driver.find_element(value="b").send_keys(Keys.RETURN)
            sleep(2)
            # profile 선택
            driver.find_elements(by=By.CLASS_NAME, value="profile-photo-container")[0].click()
            sleep(2)
            # body 태그가 로딩될때까지 대기
            body = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            # 스크롤 다운 & 업
            for i in range(8):
                body.send_keys(Keys.PAGE_DOWN)
                sleep(2)
            for i in range(8):
                body.send_keys(Keys.PAGE_UP)
                sleep(2)

            contents_wrap = driver.find_element(by=By.CLASS_NAME, value="contents_wrap")
            content_rows = contents_wrap.find_elements(by=By.CLASS_NAME, value="lists")
            for content_row in content_rows:
                # 해당 컨텐츠 ROW로 스크롤 이동
                driver.execute_script("arguments[0].scrollIntoView();", content_row)
                sleep(2)
                # vertical slide 컨텐츠 ROW만 수집
                try:
                    content_row.find_element(by=By.CLASS_NAME, value="lists__slides-vertical")
                except Exception as e:
                    print(e)
                    continue
                # 컨텐츠 ROW 타이틀 수집
                content_row_title = ""
                try:
                    content_row_title = content_row.find_element(by=By.TAG_NAME, value="h3").text
                except Exception as e:
                    print(e)
                # 컨텐츠 ROW 아이템 리스트
                content_row_items = content_row.find_elements(by=By.CLASS_NAME, value="swiper-slide")
                for item in content_row_items:
                    try:
                        video = dict()
                        link = item.find_element(by=By.TAG_NAME, value="a").get_attribute("href")
                        video['platform_id'] = link.split("/")[-1]
                        if content_row_title == "":
                            rank = dict()
                            rank['platform_code'] = "12"
                            rank['type'] = "all"
                            rank['rank'] = item.get_attribute("data-swiper-slide-index")
                            rank['platform_id'] = video['platform_id']
                            if rank not in ranks:
                                ranks.append(rank)
                        if video not in videos:
                            videos.append(video)
                    except Exception as e:
                        print(e)
                        continue
            return ranks, videos

        except Exception as e:
            raise e

