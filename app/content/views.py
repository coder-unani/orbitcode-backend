from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView, ListView, DetailView

from app.database.models import Video, Genre, Actor, Staff, CountryCode
from app.database.queryset import video as queryset
from app.utils.uploader import S3ImageUploader
from app.utils.utils import make_s3_path
from config.constraints import (
    VIDEO_CODE,
    VIDEO_PLATFORM_CODE,
    VIDEO_THUMBNAIL_CODE,
    VIDEO_ACTOR_CODE,
    VIDEO_STAFF_CODE
)
from config.settings.settings import AWS_S3_BASE_URL

DJANGO_LOGIN_URL = "/login/"
DJANGO_REDIRECT_FIELD_NAME = "next"


# Create your views here.
class Index(LoginRequiredMixin, TemplateView):
    login_url = DJANGO_LOGIN_URL
    redirect_field_name = DJANGO_REDIRECT_FIELD_NAME
    template_name = "pages/content/index.html"


class VideoList(LoginRequiredMixin, ListView):
    paginate_by = 20
    login_url = DJANGO_LOGIN_URL
    redirect_field_name = DJANGO_REDIRECT_FIELD_NAME
    model = Video
    template_name = "pages/content/video/list.html"
    context_object_name = "videos"

    def get_queryset(self):
        queryset = super().get_queryset().order_by('id')
        keyword = self.request.GET.get('q', '')
        gid = self.request.GET.get('gid', '')
        aid = self.request.GET.get('aid', '')
        sid = self.request.GET.get('sid', '')
        is_confirm = self.request.GET.get('cfm', '')
        is_delete = self.request.GET.get('del', '')
        if keyword:
            queryset = queryset.filter(title__icontains=keyword)
        if gid:
            queryset = queryset.filter(genre_list__genre_id=gid)
        if aid:
            queryset = queryset.filter(actor_list__actor_id=aid)
        if sid:
            queryset = queryset.filter(staff_list__staff_id=sid)
        if is_confirm != "" and is_confirm in ["true", "false"]:
            queryset = queryset.filter(is_confirm=(is_confirm == 'true'))
        if is_delete != "" and is_delete in ["true", "false"]:
            queryset = queryset.filter(is_delete=(is_delete == 'true'))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        context['cfm'] = self.request.GET.get('cfm', '')
        context['del'] = self.request.GET.get('del', '')
        videos = VideoList.set_thumbnail_urls_and_orientation(context['videos'])
        context['videos'] = videos

        # 페이지네이션 컨텍스트 추가
        paginator = context['paginator']
        page_obj = context['page_obj']
        is_paginated = context['is_paginated']
        context['paginator'] = paginator
        context['page_obj'] = page_obj
        context['is_paginated'] = is_paginated

        return context

    @classmethod
    def set_thumbnail_urls_and_orientation(cls, videos):
        for video in videos:
            video.is_mainimage = False
            for thumbnail in video.thumbnail.all():
                thumbnail.url = AWS_S3_BASE_URL + thumbnail.url
                if thumbnail.code == "10":
                    video.is_mainimage = True
        return videos


class VideoDetail(LoginRequiredMixin, DetailView):
    login_url = DJANGO_LOGIN_URL
    redirect_field_name = DJANGO_REDIRECT_FIELD_NAME
    model = Video
    template_name = "pages/content/video/detail.html"


class VideoEdit(LoginRequiredMixin, DetailView):
    login_url = DJANGO_LOGIN_URL
    redirect_field_name = DJANGO_REDIRECT_FIELD_NAME
    model = Video
    template_name = "pages/content/video/edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        video = self.get_object()
        context['video_code'] = VIDEO_CODE
        context['video_platform_code'] = VIDEO_PLATFORM_CODE
        context['video_actor_code'] = VIDEO_ACTOR_CODE
        context['video_staff_code'] = VIDEO_STAFF_CODE
        context['video_thumbnail_code'] = VIDEO_THUMBNAIL_CODE
        context['video_platform_code'] = VIDEO_PLATFORM_CODE
        context['video_genre_list'] = video.genre_list.all().order_by('sort', 'id')
        context['video_actor_list'] = video.actor_list.all().order_by('sort', 'code')
        context['video_staff_list'] = video.staff_list.all().order_by('sort', 'code')
        context['video_thumbnail_list'] = video.thumbnail.all().order_by('code')
        context['video_platform_list'] = video.platform.all().order_by('code')
        context['country_code_list'] = CountryCode.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        edit_type = request.POST.get('edit_type')
        video_id = kwargs.get('pk')
        video = Video.objects.get(id=video_id)
        # 비디오 정보가 없으면 리턴
        if not video:
            print('video not found')
            return render(request, self.template_name)
        # 기본정보 수정
        if edit_type == "basic":
            # 비디오 제목
            title = request.POST.get('title')
            # 비디오 타입
            video_code = request.POST.get('code')
            # 개봉일
            release = request.POST.get('release')
            # 런타임
            runtime = request.POST.get('runtime')
            # 연령 고지
            notice_age = request.POST.get('notice_age')
            # 제작사
            # production = request.POST.get('production')
            # 제작국가
            country = request.POST.get('country')
            # 시놉시스
            synopsis = request.POST.get('synopsis')
            # 관리자 확인
            is_confirm = request.POST.get('is_confirm') == "true"
            queryset.update_video(video, {
                'title': title,
                'code': video_code,
                'release': release,
                'runtime': runtime,
                'notice_age': notice_age,
                'country': country,
                'synopsis': synopsis,
                'is_confirm': is_confirm
            })
            # 비디오 상세 페이지로 리다이렉트
            return HttpResponseRedirect(reverse('content:video-detail', kwargs={'pk': video_id}))
        # 썸네일 생성/수정/삭제
        elif edit_type == "thumbnail":
            thumbnail_create = request.POST.get('thumbnail_create')
            thumbnail_delete = request.POST.get('thumbnail_delete')
            # 썸네일 생성 요청 확인
            if thumbnail_create:
                # 생성요청 썸네일 리스트
                thumbnail_create_list = thumbnail_create.split(',')
                # S3 이미지업로더 생성
                uploader = S3ImageUploader()
                # 생성요청 썸네일 리스트 Loop
                for thumbnail_id in thumbnail_create_list:
                    # 썸네일 정보 가져오기
                    code = request.POST.get('thumbnail_code_' + thumbnail_id)
                    url = request.POST.get('thumbnail_url_' + thumbnail_id)
                    upload_type = request.POST.get('thumbnail_upload_type_' + thumbnail_id)
                    # 썸네일 정보가 없으면 다음 썸네일로 이동
                    if not code or not url or not upload_type:
                        continue
                    try:
                        if upload_type == "url":
                            s3_path = make_s3_path("video", video.id, url)
                            result = uploader.upload_from_url(url, s3_path)
                        elif upload_type == "file":
                            file = request.FILES.get('thumbnail_file_' + thumbnail_id)
                            s3_path = make_s3_path("video", video.id, file.name)
                            result = uploader.upload_from_file(file, s3_path)
                        else:
                            raise Exception("Invalid upload type")
                        if not result:
                            raise Exception("Failed to upload the thumbnail")
                        # S3 업로드 성공 시 DB에 썸네일 정보 저장
                        queryset.create_video_thumbnail(video, {
                            'code': code,
                            'url': result['url'],
                            'extension': result['extension'],
                            'size': result['size'],
                            'width': result['width'],
                            'height': result['height']
                        })
                    except Exception as e:
                        print(e)
                # S3 이미지업로더 종료
                uploader.close()
            # 썸네일 삭제 요청 확인
            if thumbnail_delete:
                # 생성요청 썸네일 리스트
                thumbnail_delete_list = thumbnail_delete.split(',')
                for thumbnail_id in thumbnail_delete_list:
                    # 썸네일 삭제
                    queryset.delete_video_thumbnail(video, thumbnail_id)
            # 비디오 상세 페이지로 리다이렉트
            return HttpResponseRedirect(reverse('content:video-detail', kwargs={'pk': video_id}))
        # 시청 정보 생성/수정/삭제
        elif edit_type == "platform":
            platform_create = request.POST.get('platform_create')
            platform_delete = request.POST.get('platform_delete')
            # 시청정보 생성 요청 확인
            if platform_create:
                # 생성요청 시청정보 리스트
                platform_create_list = platform_create.split(',')
                for platform_id in platform_create_list:
                    try:
                        # 시청정보 가져오기
                        code = request.POST.get('platform_code_' + platform_id)
                        url = request.POST.get('platform_url_' + platform_id)
                        ext_id = url.split('/')[-1]
                        if not code or not code:
                            continue
                        queryset.create_video_platform(video, {
                            'code': code,
                            'ext_id': ext_id,
                            'url': url
                        })
                    except Exception as e:
                        print(e)
            # 시청정보 삭제 요청 확인
            if platform_delete:
                # 삭제요청 시청정보 리스트
                platform_delete_list = platform_delete.split(',')
                for platform_id in platform_delete_list:
                    # 시청정보 삭제
                    queryset.delete_video_platform(video, platform_id)
            # 시청정보 수정
            for platform in video.platform.all():
                try:
                    # 최종적으로 업데이트 여부 결정
                    is_update = False
                    # 시청정보 수정 요청 확인
                    code = request.POST.get('platform_code_' + str(platform.id))
                    url = request.POST.get('platform_url_' + str(platform.id))
                    ext_id = url.split('/')[-1]
                    # 시청정보가 없으면 다음 시청정보로 이동
                    if not code or not url:
                        continue
                    # 시청정보 수정
                    queryset.update_video_platform(video.platform, {
                        'code': code,
                        'ext_id': ext_id,
                        'url': url
                    })
                except Exception as e:
                    print(e)
            # 비디오 상세 페이지로 리다이렉트
            return HttpResponseRedirect(reverse('content:video-detail', kwargs={'pk': video_id}))
        elif edit_type == "genre":
            genre_create = request.POST.get('genre_create')
            genre_delete = request.POST.get('genre_delete')
            # 장르 생성 요청
            if genre_create:
                # 장르 생성 요청 리스트
                genre_create_list = genre_create.split(',')
                for genre_id in genre_create_list:
                    try:
                        # 장르 가져오기
                        genre_name = request.POST.get('genre_name_' + genre_id)
                        genre_sort = request.POST.get('genre_sort_' + genre_id)
                        if not genre_sort:
                            genre_sort = 99
                        if genre_name is None:
                            continue
                        queryset.create_video_genre(video, {
                            'name': genre_name,
                            'sort': genre_sort
                        })
                    except Exception as e:
                        raise Exception(e)
            # 장르 삭제 요청
            if genre_delete:
                try:
                    # 장르 삭제 요청 리스트
                    genre_delete_list = genre_delete.split(',')
                    for genre_id in genre_delete_list:
                        # 장르 삭제
                        queryset.delete_video_genre(video, genre_id)
                except Exception as e:
                    raise Exception(e)
            # 장르 수정
            for genre in video.genre_list.all():
                try:
                    # 장르 수정 요청 확인
                    genre_sort = request.POST.get('genre_sort_' + str(genre.id))
                    if not genre_sort:
                        genre_sort = 99
                    # 장르 정보가 없으면 다음 장르로 이동
                    if not genre_sort:
                        continue
                    # 장르 업데이트
                    queryset.update_video_genre(genre, {
                        'sort': genre_sort
                    })
                except Exception as e:
                    raise Exception(e)
            # 비디오 상세 페이지로 리다이렉트
            return HttpResponseRedirect(reverse('content:video-detail', kwargs={'pk': video_id}))
        elif edit_type == "actor":
            actor_create = request.POST.get('actor_create')
            actor_delete = request.POST.get('actor_delete')
            # 배우정보 생성 요청
            if actor_create:
                # 배우정보 생성요청 리스트
                create_list = actor_create.split(',')
                for new_id in create_list:
                    try:
                        # 배우정보 가져오기
                        actor_code = request.POST.get('actor_code_' + new_id, "")
                        actor_id = request.POST.get('actor_id_' + new_id, "")
                        actor_role = request.POST.get('actor_role_' + new_id, "")
                        actor_name = request.POST.get('actor_name_' + new_id, "")
                        actor_sort = request.POST.get('actor_sort_' + new_id, "")
                        print(actor_code, actor_id, actor_role, actor_name, actor_sort)
                        if not actor_sort:
                            actor_sort = 99
                        # 배우정보가 없으면 다음 배우정보로 이동
                        if not actor_name:
                            continue
                        queryset.create_video_actor(video, {
                            'code': actor_code,
                            'actor_id': actor_id,
                            'role': actor_role,
                            'name': actor_name,
                            'sort': actor_sort
                        })
                    except Exception as e:
                        raise Exception(e)
            # 배우정보 삭제 요청
            if actor_delete:
                try:
                    # 배우정보 삭제요청 리스트
                    actor_delete_list = actor_delete.split(',')
                    for actor_id in actor_delete_list:
                        # 배우정보 삭제
                        queryset.delete_video_actor(video, actor_id)
                except Exception as e:
                    raise Exception(e)
            # 배우정보 수정
            for actor in video.actor_list.all():
                try:
                    # 배우정보 수정 요청 확인
                    actor_code = request.POST.get('actor_code_' + str(actor.id))
                    actor_role = request.POST.get('actor_role_' + str(actor.id))
                    actor_sort = request.POST.get('actor_sort_' + str(actor.id))
                    if not actor_sort:
                        actor_sort = 99
                    # 배우정보가 없으면 다음 배우정보로 이동
                    if not actor_code or not actor_role:
                        continue
                    # 배우정보 업데이트
                    queryset.update_video_actor(actor, {
                        'code': actor_code,
                        'role': actor_role,
                        'sort': actor_sort
                    })
                except Exception as e:
                    raise Exception(e)
            # 비디오 상세 페이지로 리다이렉트
            return HttpResponseRedirect(reverse('content:video-detail', kwargs={'pk': video_id}))
        # 제작진 생성/수정/삭제
        elif edit_type == "staff":
            staff_create = request.POST.get('staff_create')
            staff_delete = request.POST.get('staff_delete')
            # 제작진 생성 요청
            if staff_create:
                # 제작진 생성요청 리스트
                create_list = staff_create.split(',')
                for new_id in create_list:
                    try:
                        # 시청정보 가져오기
                        staff_code = request.POST.get('staff_code_' + new_id)
                        staff_id = request.POST.get('staff_id_' + new_id)
                        staff_name = request.POST.get('staff_name_' + new_id)
                        staff_sort = request.POST.get('staff_sort_' + new_id)
                        if not staff_sort:
                            staff_sort = 99
                        if not staff_name:
                            continue
                        queryset.create_video_staff(video, {
                            'code': staff_code,
                            'staff_id': staff_id,
                            'name': staff_name,
                            'sort': staff_sort
                        })
                    except Exception as e:
                        raise Exception(e)
            # 제작진 삭제 요청
            if staff_delete:
                # 삭제요청 시청정보 리스트
                staff_delete_list = staff_delete.split(',')
                for staff_id in staff_delete_list:
                    # 시청정보 삭제
                    queryset.delete_video_staff(video, staff_id)
            # 제작진 수정
            for staff in video.staff_list.all():
                try:
                    # 기존 제작진 입력 정보 가져오기
                    staff_code = request.POST.get('staff_code_' + str(staff.id))
                    staff_sort = request.POST.get('staff_sort_' + str(staff.id))
                    if not staff_sort:
                        staff_sort = 99
                    # 제작진 정보가 없으면 다음 제작진으로 이동
                    if not staff_code:
                        continue
                    queryset.update_video_staff(staff, {
                        'code': staff_code,
                        'sort': staff_sort
                    })
                except Exception as e:
                    raise Exception(e)
            # 비디오 상세 페이지로 리다이렉트
            return HttpResponseRedirect(reverse('content:video-detail', kwargs={'pk': video_id}))
        else:
            return render(request, self.template_name)


class GenreList(LoginRequiredMixin, ListView):
    paginate_by = 50
    login_url = DJANGO_LOGIN_URL
    redirect_field_name = DJANGO_REDIRECT_FIELD_NAME
    model = Genre
    template_name = "pages/content/genre/list.html"

    def get_queryset(self):
        queryset = super().get_queryset().order_by('name')
        keyword = self.request.GET.get('q', '')
        if keyword:
            queryset = queryset.filter(name__icontains=keyword)
        return queryset


class ActorList(LoginRequiredMixin, ListView):
    paginate_by = 50
    login_url = DJANGO_LOGIN_URL
    redirect_field_name = DJANGO_REDIRECT_FIELD_NAME
    model = Actor
    template_name = "pages/content/actor/list.html"

    def get_queryset(self):
        queryset = super().get_queryset().order_by('name')
        keyword = self.request.GET.get('q', '')
        if keyword:
            queryset = queryset.filter(name__icontains=keyword)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        return context


class StaffList(LoginRequiredMixin, ListView):
    paginate_by = 50
    login_url = DJANGO_LOGIN_URL
    redirect_field_name = DJANGO_REDIRECT_FIELD_NAME
    model = Staff
    template_name = "pages/content/staff/list.html"

    def get_queryset(self):
        queryset = super().get_queryset().order_by('name')
        keyword = self.request.GET.get('q', '')
        if keyword:
            queryset = queryset.filter(name__icontains=keyword)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        return context
