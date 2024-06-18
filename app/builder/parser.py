from abc import ABC, abstractmethod
from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from config.properties import TVING_CONTENT_URL


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
                self.wait(2)
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
            if target is None:
                target = self.driver
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
            if target is None:
                target = self.driver
            if type == "class":
                result = target.find_elements(by=By.CLASS_NAME, value=value)
            elif type == "name":
                result = target.find_elements(by=By.NAME, value=value)
            elif type == "id":
                result = target.find_elements(by=By.ID, value=value)
            elif type == "tag":
                result = target.find_elements(by=By.TAG_NAME, value=value)
            else:
                print("Not supported type")
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
    def parse(self, html):
        pass


class TvingParser(OTTParser):
    def __init__(self):
        super().__init__("12", TVING_CONTENT_URL)

    def parse(self, content_id):
        try:
            content = dict()

            options = Options()
            options.headless = True
            # options.add_experimental_option("detach", True)
            selenium = webdriver.Chrome(options=options)
            selenium.get(self.ott_content_url + content_id)
            sleep(2)
            schema = selenium.find_element("script", attrs={"type": "application/ld+json"})
            # 컨텐츠 정보  수집
            content['platform_code'] = self.ott_type
            content['platform_id'] = content_id
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
                            "url": img_tag.get_attribute('src')
                        })
                    elif img_tag.get_attribute('src').split("/")[-1] == "480":
                        content['thumbnail'].append({
                            "type": "10",
                            "url": img_tag.get_attribute('src')
                        })
                    else:
                        continue
            print(content)
            selenium.close()
        except Exception as e:
            raise e

            # img_tags_all = soup.find_all('source')
            # print(img_tags_all)
            # for img_tag in img_tags_all:
            #     if img_tag['srcset'].find(content['platform_id']) > 0:
            #         content['thumbnail'].append(img_tag)
            # print(soup)
            # test = soup.find('article', attrs={"class": "ee4
# class TvingParser(OTTParser):
#     def __init__(self):
#         super().__init__("12", TVING_CONTENT_URL)
#
#     def parse(self, html):
#         try:
#             content = dict()
#             soup = BeautifulSoup(html, 'html.parser')
#             schema = soup.find("script", attrs={"type": "application/ld+json"})
#             schema_to_dict = eval(schema.text.strip())
#             # print(schema_to_dict)
#             # 비디오 정보 설정
#             content['type'] = schema_to_dict['@type'] == "Movie" and "10" or "11"
#             content['platform_code'] = self.ott_type
#             content['platform_id'] = schema_to_dict['url'].split("/")[-1]
#             content['title'] = ""
#             content['release'] = schema_to_dict['startDate']
#             content['notice_age'] = schema_to_dict['contentRating']
#             content['runtime'] = ""
#             content['synopsis'] = schema_to_dict['description']
#             content['genre'] = ""
#             # Actor 설정
#             content['actor'] = []
#             actor_count = 0
#             for actor in schema_to_dict['actors']:
#                 actor_type = "10"
#                 if actor_count > 1:
#                     actor_type = "11"
#                 content['actor'].append({"type": actor_type, "name": actor['name'], "role": "", "picture": "", "profile": ""})
#                 actor_count += 1
#             # Staff 설정
#             content['staff'] = []
#             for creator in schema_to_dict['creator']:
#                 content['staff'].append({"type": "11", "name": creator['name'], "picture": "", "profile": ""})
#             # Watch 설정
#             content['watch'] = []
#             content['watch'].append({"type": self.ott_type, "url": schema_to_dict['url']})
#             # Thumbnail 설정
#             content['thumbnail'] = []
#
#             imgs = soup.find_all('img')
#             print(imgs)
#             for img in imgs:
#                 print(img['src'])
#
#             # img_tags_all = soup.find_all('source')
#             # print(img_tags_all)
#             # for img_tag in img_tags_all:
#             #     if img_tag['srcset'].find(content['platform_id']) > 0:
#             #         content['thumbnail'].append(img_tag)
#             # print(soup)
#             # test = soup.find('article', attrs={"class": "ee4wkaf3"})
#             # print(test.find('img', attrs={"class": "eav61sl2"}).get('src'))
#             soup.close()
#         except Exception as e:
#             raise e

