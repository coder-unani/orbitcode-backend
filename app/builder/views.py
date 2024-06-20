from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView

from app.utils.uploader import ImageUploader, S3ImageUploader
from .builder import VideoBuilder
from .parser import OTTParser, NetflixParser, TvingParser
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
    # GET
    def get(self, request, **kwargs):
        context = dict()
        context['title'] = "넷플릭스 검색"
        search_ids = request.GET.get('search_ids')
        netflix_parser: OTTParser = NetflixParser()
        builder = VideoBuilder(netflix_parser)
        videos = builder.build(search_ids)
        builder.close()
        if videos:
            context['videos'] = videos
        # 화면 출력
        return render(request, template_name=self.template_name, context=context)
    # POST
    def post(self, request):
        platform_ids = request.POST.getlist('platform_ids')
        # 화면 출력용 context
        context = dict()
        context['summary'] = dict()
        context['messages'] = list()
        s_cnt = 0
        f_cnt = 0
        # VideoStore Init
        s3_image_uploader: ImageUploader = S3ImageUploader()
        video_store = VideoStore(s3_image_uploader)
        # platform_ids 기준으로 Loop
        for platform_id in platform_ids:
            # platform_id에 해당되는 컨텐츠
            content = eval(request.POST.get('video_' + platform_id))
            # DB저장
            result = video_store.store(content)
            if result:
                context['messages'].append({
                    "result": "success",
                    "message": "{} 저장에 성공하였습니다.".format(platform_id)
                })
                s_cnt += 1
            else:
                context['messages'].append({
                    "result": "fail",
                    "message": "{} 저장에 실패하였습니다.".format(platform_id)
                })
                f_cnt += 1
        # VideoStore Close
        video_store.close()
        # 화면 출력용 요약 정보
        context['summary'] = {"total": len(platform_ids), "success": s_cnt, "fail": f_cnt}
        # 화면 출력
        return render(request, template_name="pages/common/process-result.html", context=context)


class CollectNetflixBoxoffice(AuthView):
    # Template
    template_name = "pages/builder/collect/boxoffice.html"
    # GET
    def get(self, request, *args, **kwargs):
        # 화면 출력용 context
        context = dict()
        context['title'] = "넷플릭스 박스오피스 검색"
        context['parser'] = request.GET.get('parser')
        context['view_mode'] = request.GET.get('view_mode')
        # parser가 on일 경우 실행
        if context['parser'] == "on":
            # boxoffice 페이지 랭킹, 비디오 추출
            rank, temps = NetflixParser.boxoffice()
            # 비디오 플랫폼 코드들만 추출
            platform_ids = [video['platform_id'] for video in temps]
            # 넷플릭스 파서 생성
            tving_parser: OTTParser = NetflixParser()
            # 비디오 빌더 생성
            builder = VideoBuilder(tving_parser)
            # 비디오 빌드
            videos = builder.build(platform_ids)
            # 비디오에 썸네일 추가
            for video in videos:
                for temp in temps:
                    if video['platform_id'] == temp['platform_id'] and 'thumbnail' in temp:
                        video['thumbnail'].append(temp['thumbnail'])
            # 빌더 종료
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
        # 저장 할 데이터 platform_id List
        platform_ids = request.POST.getlist('platform_ids')
        # 화면 출력용 context
        context = dict()
        context['summary'] = dict()
        context['messages'] = list()
        s_cnt = 0
        f_cnt = 0
        # 비디오 저장 객체 생성
        s3_image_uploader: ImageUploader = S3ImageUploader()
        video_store = VideoStore(s3_image_uploader)
        # platform_ids 기준으로 Loop
        for platform_id in platform_ids:
            # platform_id에 해당되는 컨텐츠
            content = eval(request.POST.get('video_' + platform_id))
            # DB저장
            result = video_store.store(content)
            if result:
                context['messages'].append({
                    "result": "success",
                    "message": "{} 저장에 성공하였습니다.".format(platform_id)
                })
                s_cnt += 1
            else:
                context['messages'].append({
                    "result": "fail",
                    "message": "{} 저장에 실패하였습니다.".format(platform_id)
                })
                f_cnt += 1
        # VideoStore Close
        video_store.close()
        # 화면 출력용 요약 정보
        context['summary'] = {"total": len(platform_ids), "success": s_cnt, "fail": f_cnt}
        # 화면 출력
        return render(request, template_name="pages/common/process-result.html", context=context)


class CollectTving(AuthView):
    template_name = 'pages/builder/collect/index.html'

    def get(self, request, *args, **kwargs):
        context = dict()
        context['title'] = "티빙 검색"
        search_ids = request.GET.get('search_ids')
        if search_ids:
            tving_parser: OTTParser = TvingParser()
            builder = VideoBuilder(tving_parser)
            videos = builder.build(search_ids)
            builder.close()
            if videos:
                context['videos'] = videos
        return render(request, template_name=self.template_name, context=context)

    def post(self, request):
        # 저장 할 데이터 platform_ids
        platform_ids = request.POST.getlist('platform_ids')
        # 화면 출력용 context
        context = dict()
        context['summary'] = dict()
        context['messages'] = list()
        s_cnt = 0
        f_cnt = 0
        # VideoStore Init
        s3_image_uploader: ImageUploader = S3ImageUploader()
        video_store = VideoStore(s3_image_uploader)
        # platform_ids 기준으로 Loop
        for platform_id in platform_ids:
            # platform_id에 해당되는 컨텐츠
            content = eval(request.POST.get('video_' + platform_id))
            # DB저장
            result = video_store.store(content)
            if result:
                context['messages'].append({
                    "result": "success",
                    "message": "{} 저장에 성공하였습니다.".format(platform_id)
                })
                s_cnt += 1
            else:
                context['messages'].append({
                    "result": "fail",
                    "message": "{} 저장에 실패하였습니다.".format(platform_id)
                })
                f_cnt += 1
        # VideoStore Close
        video_store.close()
        # 화면 출력용 요약 정보
        context['summary'] = {"total": len(platform_ids), "success": s_cnt, "fail": f_cnt}
        # 화면 출력
        return render(request, template_name="pages/common/process-result.html", context=context)


class CollectTvingBoxoffice(AuthView):
    # Template
    template_name = "pages/builder/collect/boxoffice.html"

    def get(self, request, *args, **kwargs):
        # 화면 출력용 context
        context = dict()
        context['title'] = "넷플릭스 박스오피스 검색"
        context['parser'] = request.GET.get('parser')
        context['view_mode'] = request.GET.get('view_mode')
        # parser가 on일 경우 실행
        if context['parser'] == "on":
            boxoffice, videos = TvingParser.boxoffice()
            tving_parser: OTTParser = TvingParser()
            builder = VideoBuilder(tving_parser)
            platform_ids = [video['platform_id'] for video in videos]
            videos = builder.build(platform_ids)
            builder.close()
            if videos:
                context['videos'] = videos
        return render(request, self.template_name, context)

    def post(self, request):
        # rank 데이터
        ranks = request.POST.getlist('rank')
        # 저장 할 데이터 platform_id List
        platform_ids = request.POST.getlist('platform_ids')
        # 화면 출력용 context
        context = dict()
        context['summary'] = dict()
        context['messages'] = list()
        s_cnt = 0
        f_cnt = 0
        # 비디오 저장 객체 생성
        s3_image_uploader: ImageUploader = S3ImageUploader()
        video_store = VideoStore(s3_image_uploader)
        # platform_ids 기준으로 Loop
        for platform_id in platform_ids:
            # platform_id에 해당되는 컨텐츠
            try:
                content = eval(request.POST.get('video_' + platform_id))
                # DB저장
                result = video_store.store(content)
                if result:
                    context['messages'].append({
                        "result": "success",
                        "message": "{} 저장에 성공하였습니다.".format(platform_id)
                    })
                    s_cnt += 1
                else:
                    context['messages'].append({
                        "result": "fail",
                        "message": "{} 저장에 실패하였습니다.".format(platform_id)
                    })
                    f_cnt += 1
            except Exception as e:
                print(e)
                context['messages'].append({
                    "result": "fail",
                    "message": "{} 저장에 실패하였습니다. {}".format(platform_id, e)
                })
                f_cnt += 1
        # VideoStore Close
        video_store.close()
        # 화면 출력용 요약 정보
        context['summary'] = {"total": len(platform_ids), "success": s_cnt, "fail": f_cnt}
        # 화면 출력
        return render(request, template_name="pages/common/process-result.html", context=context)




