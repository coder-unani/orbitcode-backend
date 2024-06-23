from django.db import transaction

from app.database.models import Genre, VideoGenre
from app.database.queryset.video import create_video_all, search_videos_by_title
from app.utils.utils import make_filename
from config.constraints import AWS_S3_VIDEO_THUMBNAIL


class VideoStore:
    def __init__(self, uploader):
        # 이미지 업로더 설정
        self.uploader = uploader
        # 비디오 데이터를 만듬과 동시에 저장하려면 self.builder = VideoBuilder() 가져와서
        # self.builder.build()를 호출하면 됨
        # videos = self.builder.build(ids)

    def store(self, video):
        verified = VideoStore.verify_video_in_db(
            video['platform_code'],
            video['platform_id'],
            video['title']
        )
        if verified == "NOT_EXIST_CONTENT":
            print("NOT_EXIST_CONTENT")
            self.create_video(video)
            return True
        elif verified == "EXIST_SIMILAR_CONTENT":
            print("EXIST_SIMILAR_CONTENT")
            self.update_exist_video(video)
            return True
        elif verified == "EXIST_EXACTLY_CONTENT":
            print("EXIST_EXACTLY_CONTENT")
            return False
        else:
            return False

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
                    # UUID4 이미지 파일명 생성
                    image_filename = make_filename(thumbnail.url)
                    # S3 Object Key
                    s3_path = f"{AWS_S3_VIDEO_THUMBNAIL}{new_video.platform_code}/"
                    # S3 Object Name
                    s3_path += f"{new_video.platform_id}{new_video.id}{image_filename}"
                    # S3 업로드
                    image_result = self.uploader.upload_from_url(thumbnail.url, s3_path)
                    if not image_result:
                        return False
                    # 썸네일 정보 업데이트
                    thumbnail.url = image_result['url']
                    thumbnail.extension = image_result['extension']
                    thumbnail.size = image_result['size']
                    thumbnail.width = image_result['width']
                    thumbnail.height = image_result['height']
                    thumbnail.save()
                return True
        except Exception as e:
            raise e

    def update_exist_video(self, video):
        try:
            # 타이틀로 비디오 검색
            get_videos = search_videos_by_title(video['title'])
            if not get_videos:
                return False
            # 검색된 비디오가 있으면 첫번째 비디오 선택
            get_video = get_videos.first()
            # 업데이트 여부
            is_updated = False
            # 시청정보 업데이트
            for watch in video['watch']:
                if get_video.watch.filter(type=watch['type']).exists():
                    # 이미 업데이트 한 이력이 있으면 is_updated 변수 업데이트 후 컨티뉴
                    is_updated = True
                    continue
                get_video.watch.create(
                    type=watch['type'],
                    url=watch['url']
                )
            # 썸네일 업데이트
            for thumbnail in video['thumbnail']:
                # 이미 업데이트 한 이력이 있으면 컨티뉴
                if is_updated:
                    continue
                # 이미지 파일명 생성
                # TODO: 이미지 파일명 생성 로직을 utils로 이동
                image_filename = make_filename(thumbnail['url'])
                s3_path = f"{AWS_S3_VIDEO_THUMBNAIL}{video['platform_code']}/"
                s3_path += f"{video['platform_id']}-{get_video.id}-{image_filename}"
                upload_result = self.uploader.upload_from_url(thumbnail['url'], s3_path)
                get_video.thumbnail.create(
                    type=thumbnail['type'],
                    url=upload_result['url'],
                    extension=upload_result['extension'],
                    size=upload_result['size'],
                    width=upload_result['width'],
                    height=upload_result['height']
                )
            # 장르 정보 업데이트
            for genre in video['genre']:
                if get_video.genre.filter(name=genre['name']).exists():
                    continue
                # 장르 생성 또는 가져오기
                new_genre, created = Genre.objects.get_or_create(
                    name=genre['name']
                )
                # 비디오 장르 생성
                VideoGenre.objects.create(
                    video=get_video,
                    genre=new_genre
                )
            return True
        except Exception as e:
            raise e

    @classmethod
    def verify_video_in_db(cls, platform_code, platform_id, title):
        get_videos = search_videos_by_title(title)
        if len(get_videos) <= 0:
            return "NOT_EXIST_CONTENT"
        for video in get_videos:
            if video.platform_code == platform_code and video.platform_id == platform_id:
                return "EXIST_EXACTLY_CONTENT"
        return "EXIST_SIMILAR_CONTENT"

    def close(self):
        self.uploader.close()