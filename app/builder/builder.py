from django.forms.models import model_to_dict

from app.builder.parser import OTTParser
from app.database.queryset.video import search_video_by_platform


class VideoBuilder:
    def __init__(self, parser):
        self.parser: OTTParser = parser

    def build(self, ext_id):
        video = self.search_video(ext_id)
        return video

    def build_all(self, ids):
        if type(ids) is str:
            if ids.find(",") > 0:
                search_ids = ids.split(",")
            else:
                search_ids = [ids]
        elif type(ids) is list:
            search_ids = ids
        else:
            return False
        videos = list()
        for search_id in search_ids:
            video = self.search_video(search_id)
            videos.append(video)
        return videos

    def search_video(self, search_id):
        get_video = search_video_by_platform(self.parser.ott_code, search_id)
        if get_video:
            get_video_dict = model_to_dict(get_video)
            # 디스플레이 참고용 변수 is_db 추가
            # if get_video_dict.get('created_at'):
            #     get_video_dict['created_at'] = format_datetime_to_str(get_video_dict['created_at'])
            # if get_video_dict.get('updated_at'):
            #     get_video_dict['updated_at'] = format_datetime_to_str(get_video_dict['updated_at'])
            get_video_dict['is_db'] = True
            return get_video_dict
        parsed_content = self.parser.parse(search_id)
        # 디스플레이 참고용 변수 is_db 추가
        parsed_content['is_db'] = False
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

    def close(self):
        pass


