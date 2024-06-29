import json
import logging
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

from config.constraints import (
    NETFLIX_LOGIN_URL, NETFLIX_CONTENT_URL, DISNEY_CONTENT_URL, TVING_LOGIN_URL, TVING_CONTENT_URL, WAVVE_CONTENT_URL
)
from config.settings import settings

logger = logging.getLogger(__name__)


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
    def __init__(self, ott_code=None, ott_content_url=None):
        self.ott_code = ott_code
        self.ott_content_url = ott_content_url
    @abstractmethod
    def parse(self, content_id):
        pass


class NetflixParser(OTTParser):
    def __init__(self):
        super().__init__("10", NETFLIX_CONTENT_URL)

    def parse(self, content_id):
        soup = None
        try:
            content = dict()
            response = requests.get(self.ott_content_url + content_id)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            schema = soup.find("script", attrs={"type": "application/ld+json"})
            schema_to_dict = eval(schema.text.strip())
            # 컨텐츠 코드
            content['code'] = schema_to_dict['@type'] == "Movie" and "10" or "11"
            # 제목
            content['title'] = schema_to_dict['name']
            # 시놉시스
            content['synopsis'] = schema_to_dict['description']
            # 연령고지
            content['notice_age'] = schema_to_dict['contentRating']
            # 국가
            content['country'] = ""
            # 출시정보
            release = soup.find("span", class_="item-year")
            if release is not None:
                content['release'] = release.text.strip()
            # 상영시간
            runtime = soup.find("span", class_="item-runtime")
            if runtime is not None:
                content['runtime'] = runtime.text.strip()
            # 출연진
            content['actor'] = list()
            actor_count = 0
            for actor in schema_to_dict['actors']:
                actor_code = "10"
                if actor_count > 1:
                    actor_code = "11"
                content['actor'].append({
                    "code": actor_code, "name": actor['name'], "role": "", "picture": "", "profile": ""
                })
                actor_count += 1
            # 감독
            content['staff'] = list()
            for director in schema_to_dict['director']:
                content['staff'].append({"code": "10", "name": director['name'], "picture": "", "profile": ""})
            # 제작진
            for creator in schema_to_dict['creator']:
                content['staff'].append({"code": "11", "name": creator['name'], "picture": "", "profile": ""})
            # 장르
            content['genre'] = []
            genres = soup.find_all("a", class_="item-genres")
            for genre in genres:
                content['genre'].append({"name": genre.text.strip()})
            # 플랫폼 시청정보
            content['platform'] = [{"code": self.ott_code, "ext_id": content_id, "url": schema_to_dict['url']}]
            # 제작사
            content['production'] = []
            # 썸네일
            content['thumbnail'] = [{
                "code": "11", "url": schema_to_dict['image'], "extension": "", "size": 0, "width": 0, "height": 0
            }]
            return content
        except Exception as e:
            raise e
        finally:
            if soup:
                soup.decompose()

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
            for i in range(8):
                body.send_keys(Keys.PAGE_DOWN)
                sleep(2)
            for i in range(8):
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
                        ext_id = link.split("?")[0].split("/watch/")[1]
                        # mostWatched 컨텐츠 ROW 식별
                        if content_row_title in ["오늘 대한민국의 TOP 10 시리즈", "오늘 대한민국의 TOP 10 영화"]:
                            # mostWatched 컨텐츠는 랭킹데이터 저장
                            rank['type'] = "movie" if content_row_title == "오늘 대한민국의 TOP 10 영화" else "series"
                            rank['rank'] = int(item.find_element(by=By.TAG_NAME, value="svg").get_attribute("id").split("-")[1])
                            rank['code'] = "10"
                            rank['ext_id'] = ext_id
                            if rank not in ranks:
                                ranks.append(rank)
                            video['thumbnail'] = [{
                                "code": "10",
                                "url": item.find_element(by=By.TAG_NAME, value="img").get_attribute("src"),
                                "extension": "",
                                "size": 0,
                                "width": 0,
                                "height": 0
                            }]
                        # 랭킹 컨텐츠에 있는 이미지 추출
                        video['platform'] = [{"code": "10", "ext_id": ext_id, "url": link}]
                        # 컨텐츠 목록에 추가
                        if video not in videos:
                            videos.append(video)
                    except Exception as e:
                        print(e)
                        continue
                # for test
                # if len(videos) > 10:
                #     break
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


class DisneyParser(OTTParser):
    def __init__(self):
        super().__init__("11", DISNEY_CONTENT_URL)

    def parse(self, content_id):
        soup = None
        try:
            content = dict()
            soup = BeautifulSoup(requests.get(self.ott_content_url + content_id).text, 'html.parser')
            next_data = soup.find("script", attrs={"id": "__NEXT_DATA__"})
            json_data = json.loads(next_data.text)

            # 코드
            content_type = json_data['props']['pageProps']['metadataProps']['ldJSON']['@type']
            content['code'] = content_type == "Movie" and "10" or "11"
            # 타이틀
            content['title'] = json_data['props']['pageProps']['detailProps']['title']
            # 시놉시스
            content['synopsis'] = json_data['props']['pageProps']['heroProps']['synopsis']
            # 연령고지
            content['notice_age'] = json_data['props']['pageProps']['metadataProps']['ldJSON']['contentRating']
            # 출시일
            content['release'] = json_data['props']['pageProps']['metadataProps']['ldJSON']['datePublished']
            # 플랫폼
            links = json_data['props']['pageProps']['metadataProps']['linkTags']
            ext_id = json_data['props']['pageProps']['pageId']
            content['platform'] = [
                {"code": self.ott_code, "ext_id": ext_id, "url": link['href']}
                for link in links if link.get('rel') == "canonical"
            ]
            stats = json_data['props']['pageProps']['detailProps']['stats']
            # for stat in stats:
            #     if stat['title'] == "공개일":
            #         release = stat['value']
            #     if stat['title'] == "장르":
            #         genre = stat['value']
            #
            #         break
            # release =
            # 런타임
            # 출연진, 제작진
            cast_crews = json_data['props']['pageProps']['detailProps']['castCrew']
            for crew in cast_crews:

                if crew['title'] == "감독:":
                    content['staff'] = [
                        {"code": "10", "name": value, "picture": "", "profile": ""}
                        for value in crew['value'].replace(" ", "")
                    ]
                elif crew['title'] == "제작:":
                    content['staff'] = [
                        {"code": "12", "name": value, "picture": "", "profile": ""}
                        for value in crew['value']
                    ]
                elif crew['title'] == "출연:":
                    content['actor'] = [
                        {"code": "10", "name": value, "role": "", "picture": "", "profile": ""}
                        for value in crew['value']
                    ]
            # 플랫폼
            # 썸네일 1-3
            thumbnail = json_data['props']['pageProps']['heroProps']['backgroundImage']['mediumImage']['source'].split(",")[0]
            # 장르
            categories = json_data['props']['pageProps']['heroProps']['categories']
            content['genre'] = [
                {"name": category.replace("\u2060", "")}
                for category in categories
            ]
            print(content)
            # self.print_dict(json_data['props']['pageProps'])
            # with open(f"output_{ext_id}.txt", 'w', encoding='utf-8') as file:
            #     self.write_dict_to_file(json_data, file)

        except Exception as e:
            raise e
        finally:
            if soup:
                soup.decompose()

    def write_dict_to_file(self, d, file, depth=0):
        indent = '  ' * depth  # 깊이에 따른 들여쓰기 설정
        for key, value in d.items():
            if isinstance(value, dict):
                file.write(f"{indent}{key}:\n")
                self.write_dict_to_file(value, file, depth + 1)  # 중첩된 딕셔너리를 재귀적으로 출력
            else:
                file.write(f"{indent}{key}: {value}\n")

    def print_dict(self, d, depth=0):
        indent = '  ' * depth  # 깊이에 따른 들여쓰기 설정
        for key, value in d.items():
            if isinstance(value, dict):
                print(f"{indent}{key}:")
                self.print_dict(value, depth + 1)  # 중첩된 딕셔너리를 재귀적으로 출력
            else:
                print(f"{indent}{key}: {value}")


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
            try:
                schema = selenium.find_element(By.CSS_SELECTOR, 'head script[type="application/ld+json"]')
                schema_to_dict = json.loads(schema.get_attribute('innerHTML'))
            except Exception as e:
                print(e)
                return False

            # 컨텐츠 코드
            content['code'] = schema_to_dict['@type'] == "Movie" and "10" or "11"
            # 제목
            content['title'] = schema_to_dict['name']
            # 시놉시스 수집
            content['synopsis'] = schema_to_dict['description']
            synopsis = selenium.find_element(By.CSS_SELECTOR, 'p.ee4wkaf25').text
            if len(content['synopsis']) < len(synopsis):
                content['synopsis'] = synopsis
            # 연령고지
            content['notice_age'] = schema_to_dict['contentRating']
            # 국가
            content['country'] = ""
            # 출시정보
            content['release'] = schema_to_dict['startDate']
            # 상영시간
            content['runtime'] = ""
            tag_parent = selenium.find_element(By.CSS_SELECTOR, 'div.tag_detail')
            tag_elements = tag_parent.find_elements(By.CSS_SELECTOR, 'div.tag-blank')
            for tag_element in tag_elements:
                if tag_element.text.find("분") > -1 or tag_element.text.find("시즌") > -1:
                    content['runtime'] = tag_element.text
                    break
            # 출연진 수집
            content['actor'] = []
            actor_count = 0
            for actor in schema_to_dict['actors']:
                actor_code = "10"
                if actor_count > 1:
                    actor_code = "11"
                content['actor'].append({
                    "code": actor_code, "name": actor['name'], "role": "", "picture": "", "profile": ""
                })
                actor_count += 1
            # 제작진 수집
            content['staff'] = []
            for creator in schema_to_dict['creator']:
                content['staff'].append({"code": "11", "name": creator['name'], "picture": "", "profile": ""})
            # 장르 수집
            content['genre'] = [{"name": schema_to_dict['genre']}]
            # 플랫폼 시청정보
            content['platform'] = [{"code": self.ott_code, "ext_id": content_id, "url": selenium.current_url}]
            # 제작사
            content['production'] = []
            # 썸네일 수집
            content['thumbnail'] = []
            img_tags = selenium.find_elements(by=By.TAG_NAME, value='img')
            for img_tag in img_tags:
                if (
                    img_tag.get_attribute('src').find(content_id) > 0
                    and img_tag.get_attribute('src').find("image.tving.com") > -1
                ):
                    if img_tag.get_attribute('src').split("/")[-1] == "1280":
                        # 타이틀 정보 업데이트
                        content['title'] = img_tag.get_attribute('alt')
                        content['thumbnail'].append({
                            "code": "11",
                            "url": img_tag.get_attribute('src'),
                            "extension": "",
                            "size": 0,
                            "width": 0,
                            "height": 0
                        })
                    elif img_tag.get_attribute('src').split("/")[-1] == "480":
                        content['thumbnail'].append({
                            "code": "10",
                            "url": img_tag.get_attribute('src'),
                            "extension": "",
                            "size": 0,
                            "width": 0,
                            "height": 0
                        })
                    else:
                        continue
            print(content)
            # selenium 종료
            selenium.quit()
            return content
        except Exception as e:
            print(e)
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
                        video['platform'] = [{"code": "12", "ext_id": link.split("/")[-1], "url": link}]
                        if content_row_title == "":
                            rank = dict()
                            rank['platform_code'] = "12"
                            rank['type'] = "all"
                            rank['rank'] = item.get_attribute("data-swiper-slide-index")
                            rank['platform_id'] = link.split("/")[-1]
                            if rank not in ranks:
                                ranks.append(rank)
                        if video not in videos:
                            videos.append(video)
                    except Exception as e:
                        print(e)
                        continue
                # for test
                # if len(videos) > 10:
                #     break
            return ranks, videos

        except Exception as e:
            raise e


class WavveParser(OTTParser):
    def __init__(self):
        super().__init__("13", WAVVE_CONTENT_URL)

    def parse(self, content_url):
        driver = None
        try:
            content = dict()
            # selenium 설정
            selenium_options = Options()
            # selenium_options.add_experimental_option("detach", True) # 브라우저 종료 방지
            selenium_options.add_argument("--headless")  # 헤드리스 모드 설정
            selenium_options.add_argument("--no-sandbox")
            selenium_options.add_argument("--disable-dev-shm-usage")
            # selenium webdriver 설정
            driver = webdriver.Chrome(options=selenium_options)
            # 컨텐츠 URL 호출
            # driver.get(self.ott_content_url + content_id)
            driver.get(content_url)
            body = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            # code
            meta_type = driver.find_element(
                by=By.CSS_SELECTOR,
                value='meta[property="og:type"][data-vue-meta="ssr"]'
            ).get_attribute("content")
            if meta_type == "video.movie":
                content['code'] = "10"
            else:
                content['code'] = "11"
            # title
            meta_title = driver.find_element(
                by=By.CSS_SELECTOR,
                value='meta[property="og:title"][data-vue-meta="ssr"]'
            ).get_attribute("content")
            content['title'] = meta_title.replace("[wavve]", "").strip()
            # synopsis
            meta_description = driver.find_element(
                by=By.CSS_SELECTOR,
                value='meta[property="og:description"][data-vue-meta="ssr"]'
            ).get_attribute("content")
            content['synopsis'] = meta_description
            # platform
            meta_url = driver.find_element(
                by=By.CSS_SELECTOR,
                value='meta[property="og:url"][data-vue-meta="ssr"]'
            ).get_attribute("content")
            content['platform'] = [{"code": self.ott_code, "ext_id": meta_url.split("=")[-1], "url": meta_url}]
            # 메타 데이터 리스트
            metadata_list = driver.find_element(by=By.CLASS_NAME, value="metadata-list")
            items = metadata_list.find_elements(By.TAG_NAME, "dd")
            parsed_data = {}
            content['release'] = ""
            content['runtime'] = ""
            content['notice_age'] = ""
            for item in items:
                em_elements = item.find_elements(By.TAG_NAME, "em")
                if em_elements:
                    em_text = em_elements[0].text.strip()
                    item_text = item.text.replace(em_text, '').strip()
            # 출시일
                    if content['code'] == "10" and "개봉연도" in em_text:
                        content['release'] = item_text
            # 상영시간
                    if content['code'] == "10" and "상영시간" in em_text:
                        content['runtime'] = item_text
                    if content['code'] == "11" and "에피소드" in em_text:
                        content['runtime'] = item_text
            # 연령고지
                    elif "시청연령" in em_text:
                        img_element = item.find_element(By.TAG_NAME, "img")
                        content['notice_age'] = img_element.get_attribute(':alt').replace(' 아이콘', '')
                    elif "종류" in em_text:
                        parsed_data['code'] = item_text
            # 컨텐츠 상세정보 불러오기
            buttons = driver.find_element(by=By.CLASS_NAME, value="player-nav").find_elements(by=By.TAG_NAME, value="button")
            for button in buttons:
                if button.text == "상세정보":
                    button.click()
                    break
            detail_view = driver.find_element(by=By.CLASS_NAME, value="detail-view-box")
            # 썸네일 #1
            content['thumbnail'] = list()
            try:
                thumb_box = detail_view.find_element(by=By.CLASS_NAME, value="thumb-box")
                source_element = thumb_box.find_element(By.CSS_SELECTOR, 'picture > source')
                srcset_value = source_element.get_attribute('srcset')
                # srcset을 파싱하여 2.5x 이미지만 추출
                srcset_items = srcset_value.split(',')
                for item in srcset_items:
                    if '1.7x' in item:
                        content['thumbnail'].append({
                            "code": "10",
                            "url": item.strip().split(' ')[0],
                            "extension": "",
                            "size": 0,
                            "width": 0,
                            "height": 0,
                            "sort": "1"
                        })
                        break
            except Exception as e:
                logger.error(e)
            # 썸네일 #2
            try:
                video_container = driver.find_element(by=By.CLASS_NAME, value="video-container")
                image = video_container.find_element(by=By.CLASS_NAME, value="poster-thumb")
                content['thumbnail'].append({
                    "code": "11",
                    "url": image.get_attribute("src"),
                    "extension": "",
                    "size": 0,
                    "width": 0,
                    "height": 0,
                    "sort": "1"
                })
            except Exception as e:
                logger.error(e)
            # 디테일 정보
            detail_info = detail_view.find_element(by=By.CLASS_NAME, value="detail-info-box")
            # 시놉시스
            content['synopsis'] = detail_info.find_element(by=By.CLASS_NAME, value="detail-dsc").text
            # 출연진
            try:
                actor_elements = detail_info.find_elements(By.XPATH, '//tr[th[text()="출연"]]/td/a')
                content['actor'] = [
                    {
                        "code": "10",
                        "role": "",
                        "name": actor.text,
                        "sort": "99"
                    }
                    for actor in actor_elements
                ]
            except Exception as e:
                logger.error(e)
            # 제작진
            content['staff'] = list()
            # 감독
            try:
                director_elements = driver.find_element(By.XPATH, '//tr[th[text()="감독"]]/td/a')
                content['staff'].append({
                    "code": "10",
                    "name": director_elements.text.strip(),
                })
            except Exception as e:
                logger.error(e)
            # 작가
            try:
                writer_elements = driver.find_element(By.XPATH, '//tr[th[text()="작가"]]/td/a')
                content['staff'].append({
                    "code": "11",
                    "name": writer_elements.text.strip(),
                })
            except Exception as e:
                logger.error(e)
            # 장르
            content['genre'] = list()
            try:
                genre_elements = detail_info.find_elements(By.CSS_SELECTOR, 'tr:nth-of-type(2) td a.genre')
                content['genre'] = [
                    {
                        "name": genre.text.replace("#", "").strip(),
                    }
                    for genre in genre_elements
                ]
            except Exception as e:
                logger.error(e)
            return content
        except Exception as e:
            print(e)
        finally:
            if driver:
                driver.quit()

    @classmethod
    def boxoffice(cls):
        pass
