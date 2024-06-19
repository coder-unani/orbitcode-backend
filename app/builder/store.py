from django.db import transaction

from app.database.queryset.video import create_video_all, get_video_by_id, search_videos_by_title
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
            self.create_video(video)
            return True
        elif verified == "EXIST_SIMILAR_CONTENT":
            self.add_video_watch(video)
            self.add_video_thumbnail(video)
            return True
        elif verified == "EXIST_EXACTLY_CONTENT":
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

    def add_video_watch(self, video):
        get_video = get_video_by_id(video.id)
        if not get_video:
            return False
        for watch in video.watch.all():
            get_video.watch.add(watch).save()

    def add_video_thumbnail(self, video):
        get_video = get_video_by_id(video.id)
        if not get_video:
            return False
        for thumbnail in video.thumbnail.all():
            image_filename = make_filename(thumbnail.url)
            s3_path = f"{AWS_S3_VIDEO_THUMBNAIL}{video.type}/"
            s3_path += f"{video.type}-{video.id}-{image_filename}"
            upload_result = self.uploader.upload_from_url(thumbnail.url, s3_path)
            get_video.thumbnail.add(upload_result).save()

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