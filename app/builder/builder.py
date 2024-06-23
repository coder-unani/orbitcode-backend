from django.forms.models import model_to_dict

from app.builder.parser import OTTParser
from app.database.models import Video


class VideoBuilder:
    def __init__(self, parser):
        self.parser: OTTParser = parser

    def build(self, ids):
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
        get_videos = Video.objects.filter(platform_id=search_id)
        if get_videos.exists():
            get_video = model_to_dict(get_videos.first())
            get_video['is_db'] = True
            return get_video
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
            if not video.get('is_db'):
                video['is_db'] = False
            videos.append(video)
        return videos

    def close(self):
        pass


