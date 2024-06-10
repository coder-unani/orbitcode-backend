import json
import os
from datetime import datetime
from urllib.request import urlopen

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import render
from django.views.generic import TemplateView

from app.database.queryset.video import create_video_all, exist_video
from app.utils.logger import Logger
from app.utils.s3client import S3Client
from app.utils.utils import make_filename, save_file_from_url, get_file_extension, get_file_size
from config.properties import (
    URL_NETFLIX_CONTENT,
    AWS_S3_NETFLIX_THUMBNAIL,
    LOCAL_NETFLIX_THUMBNAIL
)
from .collectors import NetflixParser

DJANGO_LOGIN_URL = "/login/"
DJANGO_REDIRECT_FIELD_NAME = "next"


class VideoCreateView(LoginRequiredMixin, TemplateView):
    login_url = DJANGO_LOGIN_URL
    redirect_field_name = DJANGO_REDIRECT_FIELD_NAME
    # DB에 이미 존재하는지 확인
    def is_video(self, platform_id):
        return exist_video(platform_id=platform_id)
    # DB에 비디오 객체 생성
    def create_video_objects(self, new_video):
        try:
            # 트랜잭션 시작
            with transaction.atomic():
                # 비디오 생성
                video = create_video_all(new_video)
                # 비디오 생성 실패시 False 반환
                if not video:
                    return False
                # 비디오 썸네일 S3 업로드
                s3client = S3Client()
                for thumbnail in video.thumbnail.all():
                    file_name = make_filename(thumbnail.url)
                    file_path = os.path.join(LOCAL_NETFLIX_THUMBNAIL, file_name)
                    if not save_file_from_url(thumbnail.url, file_path):
                        continue
                    if not s3client.upload_file(file_path, AWS_S3_NETFLIX_THUMBNAIL):
                        continue
                    thumbnail.url = os.path.join(AWS_S3_NETFLIX_THUMBNAIL, file_name)
                    thumbnail.extension = get_file_extension(file_name)
                    thumbnail.size = get_file_size(file_path)
                    thumbnail.save()
                # S3 클라이언트 종료
                s3client.close()
            return True
        except Exception as e:
            Logger.error_log(self.__class__.__name__, "Failed to create video objects. {}".format(e))
            return False


class Index(LoginRequiredMixin, TemplateView):
    login_url = DJANGO_LOGIN_URL
    redirect_field_name = DJANGO_REDIRECT_FIELD_NAME
    template_name = "pages/builder/index.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {})


class CollectNetflix(VideoCreateView):
    # Template
    template_name = 'pages/builder/collect/netflix/index.html'
    # GET
    def get(self, request, **kwargs):
        search_ids = request.GET.get('search_ids')
        context = dict()
        if search_ids:
            search_ids_to_list = search_ids.split(',')
            video_ids = []
            videos = []
            parser = NetflixParser()
            for search_id in search_ids_to_list:
                content = parser.get_content_netflix(search_id)
                if content:
                    video_ids.append(search_id)
                    videos.append(content)
            parser.close()
            context['videos'] = videos
        return render(request, template_name=self.template_name, context=context)
    # POST
    def post(self, request):
        platform_ids = request.POST.getlist('platform_ids')
        context = dict()
        save_count = 0
        fail_count = 0
        context['summary'] = dict()
        context['messages'] = list()
        if len(platform_ids) > 0:
            for platform_id in platform_ids:
                content = eval(request.POST.get('video_' + platform_id))
                if self.is_video(platform_id):
                    context['messages'].append({
                        "result": "fail",
                        "message": "{} 이미 존재하는 데이터입니다.".format(platform_id)
                    })
                    fail_count += 1
                    continue
                if self.create_video_objects(content):
                    context['messages'].append({
                        "result": "success",
                        "message": "{} 저장에 성공하였습니다.".format(platform_id)
                    })
                    save_count += 1
                else:
                    context['messages'].append({
                        "result": "fail",
                        "message": "{} 저장에 실패하였습니다.".format(platform_id)
                    })
                    fail_count += 1
        else:
            context['messages'].append({"result": "fail", "message": "저장할 데이터가 없습니다."})
        context['summary'] = {"total": len(platform_ids), "success": save_count, "fail": fail_count}
        return render(request, template_name="pages/common/process-result.html", context=context)


class CollectNetflixBoxoffice(VideoCreateView):
    # Template
    template_name = 'pages/builder/collect/netflix/boxoffice.html'
    # 데이터 저장 파일 경로
    data_path = "data/video/"
    netflix_videos = "netflix_{}.json".format(datetime.now().strftime("%Y%m%d%H"))
    netflix_ranks = "netflix_ranks_{}.json".format(datetime.now().strftime("%Y%m%d%H"))
    path_file_videos = os.path.join(data_path, netflix_videos)
    path_file_ranks = os.path.join(data_path, netflix_ranks)
    # GET
    def get(self, request, **kwargs):
        parser = request.GET.get('parser')
        view_mode = "html"
        # parser == on 데이터 파싱 시작
        if parser == "on":
            Logger.info_log(
                self.__class__.__name__,
                "START. Netflix box office data parsing. parser={}, view_mode={}".format(parser, view_mode)
            )
            # 뷰 모드 설정
            if request.GET.get('view_mode'):
                view_mode = request.GET.get('view_mode')
            # 파일에서 컨텐츠 로드
            videos = self.load_from_file(self.path_file_videos)
            ranks = self.load_from_file(self.path_file_ranks)
            # 파일이 없으면 넷플릭스 파싱
            if videos is None or ranks is None:
                parser = NetflixParser()
                videos, ranks = parser.get_contents()
                parser.close()
                # contents 가져오기
                parse_videos = []
                for video in videos:
                    if self.is_video(video['platform_id']):
                        # TODO: 이미 존재하는 컨텐츠 DB에 있는데 데이터 불러오기
                        continue
                    parser = NetflixParser()
                    url = URL_NETFLIX_CONTENT + "/" + video['platform_id']
                    with urlopen(url) as response:
                        html = response.read()
                    new_video = parser.parse_content(html)
                    parser.close()
                    if video.get('thumbnail') and new_video.get('thumbnail'):
                        new_video['thumbnail'].append(video['thumbnail'])
                    parse_videos.append(new_video)
                videos = parse_videos
                parser.close()
                # 가져온 컨텐츠를 파일에 저장
                self.save_to_file(self.path_file_videos, videos)
                self.save_to_file(self.path_file_ranks, ranks)

            # contents 분리
            rank_movies = []
            rank_series = []

            for rank in ranks:
                if rank['type'] == "10":
                    rank_movies.append(rank)
                elif rank['type'] == "11":
                    rank_series.append(rank)
            movies = sorted(rank_movies, key=lambda x: x['rank'])
            series = sorted(rank_series, key=lambda x: x['rank'])

            # context 생성
            context = {
                "view_mode": view_mode,
                "parser": parser,
                "ranks": {
                    "movies": movies,
                    "series": series
                },
                "videos": videos
            }

            Logger.info_log(self.__class__.__name__, "END. Netflix box office data parsing")
            # 화면 출력
            return render(request, template_name=self.template_name, context=context)

        else:
            # 화면 출력
            return render(request, template_name=self.template_name)

    def post(self, request):
        Logger.info_log(self.__class__.__name__, "START. Save Netflix box office data to database.")
        # 저장 할 데이터 platform_ids
        platform_ids = request.POST.getlist('platform_ids')
        # 화면 출력용 context
        context = dict()
        save_count = 0
        fail_count = 0
        context['summary'] = dict()
        context['messages'] = list()
        # platform_id 기준으로 컨텐츠 저장
        for platform_id in platform_ids:
            # platform_id 에 해당되는 컨텐츠
            video = eval(request.POST.get('video_' + platform_id))
            # 이미 DB에 존재하는지 확인
            if self.is_video(video['platform_id']):
                context['messages'].append({
                    "result": "fail",
                    "message": "{} 이미 존재하는 데이터입니다.".format(platform_id)
                })
                fail_count += 1
                continue
            # 데이터 생성
            video = self.create_video_objects(video)
            if video:
                context['messages'].append({
                    "result": "success",
                    "message": "{} 저장에 성공하였습니다.".format(platform_id)
                })
                fail_count += 1
            else:
                context['messages'].append({
                    "result": "fail",
                    "message": "{} 저장에 실패하였습니다.".format(platform_id)
                })
                fail_count += 1
        Logger.info_log(self.__class__.__name__, "END. Save Netflix box office data to database.")
        # 화면 출력용 요약 정보
        context['summary'] = {"total": len(platform_ids), "success": save_count, "fail": fail_count}
        # 화면 출력
        return render(request, template_name="pages/common/process-result.html", context=context)
    # 파일 불러오기
    def load_from_file(self, path_file):
        try:
            with open(path_file, "r") as file:
                contents = json.load(file)
            if len(contents) > 0 or contents is not None:
                Logger.info_log(self.__class__.__name__, "Load from file successful. file={}".format(path_file))
            else:
                Logger.error_log(self.__class__.__name__, "Failed to load from file. file={}".format(path_file))
            return contents
        except Exception as e:
            Logger.error_log(self.__class__.__name__, "Failed to load from file. file={}, error={}".format(path_file, e))
            return None
    # 파일 저장
    def save_to_file(self, path_file, content):
        try:
            with open(path_file, "w") as file:
                json.dump(obj=content, fp=file, indent=4)
            Logger.info_log(self.__class__.__name__, "Save to file success. file={}".format(path_file))
            return True
        except Exception as e:
            Logger.error_log(self.__class__.__name__, "Failed to save to file. file={} / e={}".format(path_file, e))
            return False





