import ast

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView

from app.utils.uploader import ImageUploader, S3ImageUploader
from .builder import VideoBuilder
from .parser import OTTParser, NetflixParser, DisneyParser, TvingParser, WavveParser
from .store import VideoStore

DJANGO_LOGIN_URL = "/login/"
DJANGO_REDIRECT_FIELD_NAME = "next"


class AuthView(LoginRequiredMixin, TemplateView):
    login_url = DJANGO_LOGIN_URL
    redirect_field_name = DJANGO_REDIRECT_FIELD_NAME


class Index(LoginRequiredMixin, TemplateView):
    login_url = DJANGO_LOGIN_URL
    redirect_field_name = DJANGO_REDIRECT_FIELD_NAME
    template_name = "pages/builder/index.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {})


class CollectNetflix(AuthView):
    # Template
    template_name = 'pages/builder/collect/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "넷플릭스 검색"
        return context

    # GET
    def get(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        search_ids = request.GET.get('search_ids')
        if search_ids:
            parser: OTTParser = NetflixParser()
            builder = VideoBuilder(parser)
            videos = list()
            for search_id in search_ids.split(","):
                video = builder.build(search_id)
                if video and video not in videos:
                    videos.append(video)
            builder.close()
            if videos:
                context['videos'] = videos
        # 화면 출력
        return render(request, template_name=self.template_name, context=context)
    # POST
    def post(self, request):
        ext_ids = request.POST.getlist('ext_ids')
        # 빈 값 제거
        ext_ids = [item for item in ext_ids if item]
        # 화면 출력용 context
        context = dict()
        context['summary'] = dict()
        context['messages'] = list()
        s_cnt = 0
        f_cnt = 0
        # VideoStore Init
        s3_image_uploader: ImageUploader = S3ImageUploader()
        video_store = VideoStore(s3_image_uploader)
        # ext_ids 기준으로 Loop
        for ext_id in ext_ids:
            try:
                # ext_id에 해당되는 form data
                form_video = request.POST.get('video_' + ext_id)
                if not form_video:
                    continue
                # form data를 dict로 변환
                content = ast.literal_eval(form_video)
                # 이미 저장된 컨텐츠는 저장하지 않음
                if content.get('is_db', False):
                    context['messages'].append({
                        "result": "fail",
                        "message": f"{ext_id} 이미 저장되어 있는 컨텐츠 입니다."
                    })
                    f_cnt += 1
                    continue
                # DB저장
                result = video_store.store(content)
                # 저장 결과
                if result:
                    context['messages'].append({
                        "result": "success",
                        "message": f"{ext_id} 컨텐츠 저장에 성공 했습니다."
                    })
                    s_cnt += 1
                else:
                    context['messages'].append({
                        "result": "fail",
                        "message": f"{ext_id} 저장에 실패하였습니다."
                    })
                    f_cnt += 1
            except Exception as e:
                print(e)
        # VideoStore Close
        video_store.close()
        # 화면 출력용 요약 정보
        context['summary'] = {"total": len(ext_ids), "success": s_cnt, "fail": f_cnt}
        # 화면 출력
        return render(request, template_name="pages/common/process-result.html", context=context)


class CollectNetflixBoxoffice(AuthView):
    # Template
    template_name = "pages/builder/collect/boxoffice.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "넷플릭스 박스오피스 검색"
        return context

    # GET
    def get(self, request, *args, **kwargs):
        # 화면 출력용 context
        context = self.get_context_data(**kwargs)
        context['parser'] = request.GET.get('parser')
        context['view_mode'] = request.GET.get('view_mode')
        # parser가 on일 경우 실행
        if context['parser'] == "on":
            # boxoffice 페이지 랭킹, 비디오 추출
            rank, boxoffice_videos = NetflixParser.boxoffice()
            # 넷플릭스 파서 생성
            tving_parser: OTTParser = NetflixParser()
            # 비디오 빌더 생성
            builder = VideoBuilder(tving_parser)
            # 비디오 생성
            videos = list()
            for video in boxoffice_videos:
                platforms = video.get('platform', [])
                thumbnails = video.get('thumbnail', [])
                for platform in platforms:
                    build_video = builder.build(platform['ext_id'])
                    if build_video['is_db']:
                        continue
                    build_video['thumbnail'].extend(thumbnails)
                    videos.append(build_video)
            # 비디오 빌더 종료
            builder.close()
            # 화면 출력용 context
            context['rank'] = rank
            context['videos'] = videos
        # 화면 출력
        return render(request, template_name=self.template_name, context=context)
    # POST
    def post(self, request):
        # rank 데이터
        ranks = request.POST.getlist('rank')
        # HTML Form에서 전달받은 ext_id 목록
        ext_ids = request.POST.getlist('ext_ids')
        # 빈 값 제거
        ext_ids = [item for item in ext_ids if item]
        # 화면 출력용 context
        context = dict()
        context['summary'] = dict()
        context['messages'] = list()
        s_cnt = 0
        f_cnt = 0
        # 비디오 저장 객체 생성
        s3_image_uploader: ImageUploader = S3ImageUploader()
        video_store = VideoStore(s3_image_uploader)
        # ext_ids 기준으로 Loop
        for ext_id in ext_ids:
            try:
                # ext_id에 해당되는 form data
                form_video = request.POST.get('video_' + ext_id)
                if not form_video:
                    continue
                # form data를 dict로 변환
                content = ast.literal_eval(form_video)
                # 이미 저장된 컨텐츠는 저장하지 않음
                if content.get('is_db', False):
                    context['messages'].append({
                        "result": "fail",
                        "message": f"{ext_id} 이미 저장되어 있는 컨텐츠 입니다."
                    })
                    f_cnt += 1
                    continue
                # DB저장
                result = video_store.store(content)
                # 저장 결과
                if result:
                    context['messages'].append({
                        "result": "success",
                        "message": f"{ext_id} 컨텐츠 저장에 성공 했습니다."
                    })
                    s_cnt += 1
                else:
                    context['messages'].append({
                        "result": "fail",
                        "message": f"{ext_id} 저장에 실패하였습니다."
                    })
                    f_cnt += 1
            except Exception as e:
                print(e)
        # VideoStore Close
        video_store.close()
        # 화면 출력용 요약 정보
        context['summary'] = {"total": len(ext_ids), "success": s_cnt, "fail": f_cnt}
        # 화면 출력
        return render(request, template_name="pages/common/process-result.html", context=context)


class CollectDisney(AuthView):
    template_name = 'pages/builder/collect/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "디즈니플러스 검색"
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        search_ids = request.GET.get('search_ids')
        if search_ids:
            parser: OTTParser = DisneyParser()
            builder = VideoBuilder(parser)
            videos = list()
            for search_id in search_ids.split(","):
                video = builder.build(search_id)
                if video and video not in videos:
                    videos.append(video)
            builder.close()
            if videos:
                context['videos'] = videos
        return render(request, template_name=self.template_name, context=context)


class CollectTving(AuthView):
    template_name = 'pages/builder/collect/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "티빙 검색"
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        search_ids = request.GET.get('search_ids')
        if search_ids:
            parser: OTTParser = TvingParser()
            builder = VideoBuilder(parser)
            videos = list()
            for search_id in search_ids.split(","):
                video = builder.build(search_id)
                if video and video not in videos:
                    videos.append(video)
            builder.close()
            if videos:
                context['videos'] = videos
        return render(request, template_name=self.template_name, context=context)

    def post(self, request):
        ext_ids = request.POST.getlist('ext_ids')
        # 빈 값 제거
        ext_ids = [item for item in ext_ids if item]
        # 화면 출력용 context
        context = dict()
        context['summary'] = dict()
        context['messages'] = list()
        s_cnt = 0
        f_cnt = 0
        # VideoStore Init
        s3_image_uploader: ImageUploader = S3ImageUploader()
        video_store = VideoStore(s3_image_uploader)
        # ext_ids 기준으로 Loop
        for ext_id in ext_ids:
            try:
                # ext_id에 해당되는 form data
                form_video = request.POST.get('video_' + ext_id)
                print("form_video", form_video)
                if not form_video:
                    continue
                # form data를 dict로 변환
                content = ast.literal_eval(form_video)
                print("content", content)
                # 이미 저장된 컨텐츠는 저장하지 않음
                if content.get('is_db', False):
                    context['messages'].append({
                        "result": "fail",
                        "message": f"{ext_id} 이미 저장되어 있는 컨텐츠 입니다."
                    })
                    f_cnt += 1
                    continue
                # DB저장
                result = video_store.store(content)
                # 저장 결과
                if result:
                    context['messages'].append({
                        "result": "success",
                        "message": f"{ext_id} 컨텐츠 저장에 성공 했습니다."
                    })
                    s_cnt += 1
                else:
                    context['messages'].append({
                        "result": "fail",
                        "message": f"{ext_id} 저장에 실패하였습니다."
                    })
                    f_cnt += 1
            except Exception as e:
                print(e)
        # VideoStore Close
        video_store.close()
        # 화면 출력용 요약 정보
        context['summary'] = {"total": len(ext_ids), "success": s_cnt, "fail": f_cnt}
        # 화면 출력
        return render(request, template_name="pages/common/process-result.html", context=context)


class CollectTvingBoxoffice(AuthView):
    # Template
    template_name = "pages/builder/collect/boxoffice.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "티빙 박스오피스 검색"
        return context

    def get(self, request, *args, **kwargs):
        # 화면 출력용 context
        context = self.get_context_data(**kwargs)
        context['parser'] = request.GET.get('parser')
        context['view_mode'] = request.GET.get('view_mode')
        # parser가 on일 경우 실행
        if context['parser'] == "on":
            rank, boxoffice_videos = TvingParser.boxoffice()
            tving_parser: OTTParser = TvingParser()
            builder = VideoBuilder(tving_parser)
            # 비디오 생성
            videos = list()
            for video in boxoffice_videos:
                platforms = video.get('platform', [])
                for platform in platforms:
                    build_video = builder.build(platform['ext_id'])
                    if not build_video or build_video.get('is_db', False):
                        continue
                    videos.append(build_video)
            # 비디오 빌더 종료
            builder.close()
            if videos:
                context['videos'] = videos
        return render(request, self.template_name, context)

    # POST
    def post(self, request):
        # rank 데이터
        ranks = request.POST.getlist('rank')
        # HTML Form에서 전달받은 ext_id 목록
        ext_ids = request.POST.getlist('ext_ids')
        # 빈 값 제거
        ext_ids = [item for item in ext_ids if item]
        # 화면 출력용 context
        context = dict()
        context['summary'] = dict()
        context['messages'] = list()
        s_cnt = 0
        f_cnt = 0
        # 비디오 저장 객체 생성
        s3_image_uploader: ImageUploader = S3ImageUploader()
        video_store = VideoStore(s3_image_uploader)
        # ext_ids 기준으로 Loop
        for ext_id in ext_ids:
            try:
                # ext_id에 해당되는 form data
                form_video = request.POST.get('video_' + ext_id)
                if not form_video:
                    continue
                # form data를 dict로 변환
                content = ast.literal_eval(form_video)
                # 이미 저장된 컨텐츠는 저장하지 않음
                if content.get('is_db', False):
                    context['messages'].append({
                        "result": "fail",
                        "message": f"{ext_id} 이미 저장되어 있는 컨텐츠 입니다."
                    })
                    f_cnt += 1
                    continue
                # DB저장
                result = video_store.store(content)
                # 저장 결과
                if result:
                    context['messages'].append({
                        "result": "success",
                        "message": f"{ext_id} 컨텐츠 저장에 성공 했습니다."
                    })
                    s_cnt += 1
                else:
                    context['messages'].append({
                        "result": "fail",
                        "message": f"{ext_id} 저장에 실패하였습니다."
                    })
                    f_cnt += 1
            except Exception as e:
                print(e)
        # VideoStore Close
        video_store.close()
        # 화면 출력용 요약 정보
        context['summary'] = {"total": len(ext_ids), "success": s_cnt, "fail": f_cnt}
        # 화면 출력
        return render(request, template_name="pages/common/process-result.html", context=context)


class CollectWavve(AuthView):
    template_name = 'pages/builder/collect/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "웨이브 검색"
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        search_ids = request.GET.get('search_ids')
        if search_ids:
            parser: OTTParser = WavveParser()
            builder = VideoBuilder(parser)
            videos = list()
            for search_id in search_ids.split(","):
                video = builder.build(search_id)
                if video and video not in videos:
                    videos.append(video)
            builder.close()
            if videos:
                context['videos'] = videos
        return render(request, template_name=self.template_name, context=context)


