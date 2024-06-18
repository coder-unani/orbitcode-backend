import requests
from django.db import transaction

from app.builder.parser import OTTParser
from app.database.queryset.video import create_video_all, search_videos_by_title
from app.utils.uploader import ImageUploader


class VideoBuilder:
    def __init__(self, parser, uploader):
        self.parser: OTTParser = parser
        self.img_uploader: ImageUploader = uploader

    def build(self, ids):
        search_ids = list()
        if type(ids) is str:
            if ids.find(",") > 0:
                search_ids = ids.split(",")
            else:
                search_ids = [ids]
        elif type(ids) is list:
            search_ids = ids
        else:
            return False

        for search_id in search_ids:
            print(search_id)
            video = self.search_video(search_id)
        #     is_exist = self.verify_content_in_db(video['platform_code'], video['platform_id'], video['title'])
        #     if is_exist == "EXIST_EXACTLY_CONTENT":
        #         continue
        #     elif is_exist == "EXIST_SIMILAR_CONTENT":
        #         self.add_thumbnail(video)
        #         self.add_watch(video)
        #     elif is_exist == "NOT_EXIST_CONTENT":
        #         self.create_video(video)

        return True

    def search_video(self, search_id):
        # 컨텐트 URL 설정
        content_url = self.parser.ott_content_url
        if not content_url.endswith("/"):
            content_url += "/"
        content_url += search_id
        # 컨텐트 HTML 가져오기
        response = requests.get(content_url)
        response.raise_for_status()
        # 컨텐트 파싱
        # parsed_content = self.parser.parse(response.text)
        parsed_content = self.parser.parse(search_id)
        return parsed_content

    def search_videos(self, search_ids):
        videos = list()
        if type(search_ids) is str:
            if search_ids.find(",") > 0:
                search_ids = search_ids.split(",")
            else:
                search_ids = [search_ids]
        for search_id in search_ids:
            video = self.search_video(search_id)
            videos.append(video)
        return videos

    def verify_content_in_db(self, platform_code, platform_id, title):
        get_videos = search_videos_by_title(title)
        if len(get_videos) <= 0:
            return "NOT_EXIST_CONTENT"
        for video in get_videos:
            if video.platform_code == platform_code and video.platform_id == platform_id:
                return "EXIST_EXACTLY_CONTENT"
        return "EXIST_SIMILAR_CONTENT"

    def create_video(self, video):
        try:
            # 트랜잭션 시작
            with transaction.atomic():
                # 비디오 생성
                new_video = create_video_all(video)
                # 비디오 생성 실패시 False 반환
                if not new_video:
                    return False
                for thumbnail in new_video.thumbnail.all():
                    imageResult = self.img_uploader.upload_from_url(thumbnail.url, thumbnail.url)
                    if not imageResult:
                        return False
                    thumbnail.url = imageResult['url']
                    thumbnail.extension = imageResult['extension']
                    thumbnail.size = imageResult['size']
                    thumbnail.save()
            return True
        except Exception as e:
            raise e

    def add_thumbnail(self, video):
        get_video = search_videos_by_title(video.title)
        if len(get_video) <= 0:
            return False
        get_video.thumbnail.create(
            type=video.thumbnail['type'],
            url=video.thumbnail['url'],
            extension=video.thumbnail['extension'],
            size=video.thumbnail['size'],
        ).save()
        pass

    def add_watch(self, content):
        pass