from django.db import transaction

from app.database.queryset.video import (
    create_video_object_all,
    create_video_genre,
    create_video_platform,
    create_video_thumbnail,
    search_video_by_title,
    search_video_by_platform,
    exist_video_genre
)
from app.utils.utils import make_s3_path


class VideoStore:
    def __init__(self, uploader):
        # 이미지 업로더 설정
        self.uploader = uploader
        # 비디오 데이터를 만듬과 동시에 저장하려면 self.builder = VideoBuilder() 가져와서
        # self.builder.build()를 호출하면 됨
        # videos = self.builder.build(ids)

    def store(self, video):
        try:
            # 일치하는 플랫폼의 비디오가 있는지 확인
            for platform in video['platform']:
                get_video = search_video_by_platform(platform['code'], platform['ext_id'])
                # 일치하는 비디오가 있으면 프로세스 종료
                if get_video:
                    return False
            # 비디오 제목으로 일치하는 비디오 확인
            get_video = search_video_by_title(video['title'])
            # 일치하는 비디오가 있으면 비디오 업데이트
            if get_video:
                self.update_video(get_video, video)
                return True
            # 일치하는 비디오가 없으면 비디오 생성
            else:
                self.create_video(video)
                return True
        except Exception as e:
            print(e)
            raise e

    def create_video(self, video):
        try:
            # 트랜잭션 시작
            with transaction.atomic():
                # 비디오 생성
                new_video = create_video_object_all(video)
                # 비디오 생성 실패시 False 반환
                if not new_video:
                    return False
                for thumbnail in new_video.thumbnail.all():
                    # s3 경로 생성
                    s3_path = make_s3_path("video", new_video.id, thumbnail.url)
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

    def update_video(self, get_video, video):
        try:
            if not get_video:
                return False
            # 비디오에 플랫폼 정보 추가
            for platform in video['platform']:
                create_video_platform(get_video, platform)
            # 비디오에 썸네일 정보 추가
            for thumbnail in video['thumbnail']:
                s3_path = make_s3_path("video", get_video.id, thumbnail['url'])
                s3_upload_result = self.uploader.upload_from_url(thumbnail['url'], s3_path)
                create_video_thumbnail(get_video, {
                    'code': thumbnail['code'],
                    'url': s3_upload_result['url'],
                    'extension': s3_upload_result['extension'],
                    'size': s3_upload_result['size'],
                    'width': s3_upload_result['width'],
                    'height': s3_upload_result['height']
                })
            # 비디오에 장르 정보 추가
            for genre in video['genre']:
                if not exist_video_genre(get_video, genre):
                    create_video_genre(get_video, genre)
            return True
        except Exception as e:
            raise e

    def close(self):
        self.uploader.close()
