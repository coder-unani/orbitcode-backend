from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView, ListView, DetailView

from app.database.models import Video, Genre, Actor, Staff
from app.utils.uploader import S3ImageUploader
from app.utils.utils import make_filename
from config.constraints import (
    AWS_S3_VIDEO_THUMBNAIL,
    THUMBNAIL_BASE_URL,
    VIDEO_PLATFORM_CHOICES,
    VIDEO_TYPE_CHOICES,
    VIDEO_THUMBNAIL_TYPE,
    VIDEO_ACTOR_TYPE,
    VIDEO_STAFF_TYPE
)

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
        queryset = super().get_queryset().order_by('-created_at')
        keyword = self.request.GET.get('q', '')
        is_confirm = self.request.GET.get('cfm', '')
        is_delete = self.request.GET.get('del', '')
        if keyword:
            queryset = queryset.filter(title__icontains=keyword)
        if is_confirm != "" and is_confirm in ["true", "false"]:
            queryset = queryset.filter(is_confirm=(is_confirm == 'true'))
        if is_delete != "" and is_delete in ["true", "false"]:
            queryset = queryset.filter(is_delete=(is_delete == 'true'))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q')
        context['cfm'] = self.request.GET.get('cfm')
        context['del'] = self.request.GET.get('del')
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
            video.is_vertical = False
            for thumbnail in video.thumbnail.all():
                thumbnail.url = THUMBNAIL_BASE_URL + thumbnail.url
                if thumbnail.type == "10":
                    video.is_vertical = True
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
        context['video_platform'] = VIDEO_PLATFORM_CHOICES
        context['video_type'] = VIDEO_TYPE_CHOICES
        context['video_thumbnail_type'] = VIDEO_THUMBNAIL_TYPE
        context['video_actor_type'] = VIDEO_ACTOR_TYPE
        context['video_staff_type'] = VIDEO_STAFF_TYPE
        context['video_genre_list'] = video.genre_list.all().order_by('id')
        context['video_actor_list'] = video.actor_list.all().order_by('type')
        context['video_staff_list'] = video.staff_list.all().order_by('type')
        context['video_thumbnail_list'] = video.thumbnail.all().order_by('type')
        context['video_watch_list'] = video.watch.all().order_by('type')

        return context

    def post(self, request, *args, **kwargs):
        edit_type = request.POST.get('edit_type')
        video_id = kwargs.get('pk')
        video = Video.objects.get(id=video_id)
        # 비디오 정보가 없으면 리턴
        if not video:
            print('video not found')
            return render(request, self.template_name)
        if edit_type == "basic":
            # 비디오 제목
            title = request.POST.get('title')
            if title:
                video.title = title
            # 비디오 타입
            video_type = request.POST.get('type')
            if video_type:
                video.type = video_type
            # 개봉일
            release = request.POST.get('release')
            if release:
                video.release = release
            # 런타임
            runtime = request.POST.get('runtime')
            if runtime:
                video.runtime = runtime
            # 연령 고지
            notice_age = request.POST.get('notice_age')
            if notice_age:
                video.notice_age = notice_age
            # 관리자 확인
            is_confirm = request.POST.get('is_confirm')
            if is_confirm:
                video.is_confirm = is_confirm == "true"
            else:
                video.is_confirm = False
            video.save()
            # 비디오 상세 페이지로 리다이렉트
            return HttpResponseRedirect(reverse('content:video-detail', kwargs={'pk': video_id}))
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
                    thumbnail_type = request.POST.get('thumbnail_type_' + thumbnail_id)
                    thumbnail_url = request.POST.get('thumbnail_url_' + thumbnail_id)
                    try:
                        # 썸네일 저장
                        file_name = make_filename(thumbnail_url)
                        # 썸네일 S3 업로드 경로 생성
                        s3_path = f"{AWS_S3_VIDEO_THUMBNAIL}{video.platform_code}/{video.platform_id}{video.id}{file_name}"
                        result = uploader.upload_from_url(thumbnail_url, s3_path)
                        if not result:
                            raise Exception("Failed to upload the thumbnail")
                        # S3 업로드 성공 시 DB에 썸네일 정보 저장
                        thumbnail = video.thumbnail.create(
                            type=thumbnail_type,
                            url=result['url'],
                            extension=result['extension'],
                            size=result['size'],
                            width=result['width'],
                            height=result['height']
                        )
                        thumbnail.save()
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
                    thumbnail = video.thumbnail.get(id=thumbnail_id)
                    thumbnail.delete()
            # 비디오 상세 페이지로 리다이렉트
            return HttpResponseRedirect(reverse('content:video-detail', kwargs={'pk': video_id}))
        elif edit_type == "watch":
            watch_create = request.POST.get('watch_create')
            watch_delete = request.POST.get('watch_delete')
            # 시청정보 생성 요청 확인
            if watch_create:
                # 생성요청 시청정보 리스트
                watch_create_list = watch_create.split(',')
                for watch_id in watch_create_list:
                    try:
                        # 시청정보 가져오기
                        watch_type = request.POST.get('watch_type_' + watch_id)
                        watch_url = request.POST.get('watch_url_' + watch_id)
                        watch = video.watch.create(
                            type=watch_type,
                            url=watch_url
                        )
                        watch.save()
                    except Exception as e:
                        print(e)
            # 시청정보 삭제 요청 확인
            if watch_delete:
                # 삭제요청 시청정보 리스트
                watch_delete_list = watch_delete.split(',')
                for watch_id in watch_delete_list:
                    # 시청정보 삭제
                    watch = video.watch.get(id=watch_id)
                    watch.delete()
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
                        # 기존 장르에 없으면 생성
                        new_genre = Genre.objects.get_or_create(name=genre_name)
                        # 비디오에 장르 추가
                        video.genre_list.create(
                            genre=new_genre
                        )
                    except Exception as e:
                        raise Exception(e)
            # 장르 삭제 요청
            if genre_delete:
                try:
                    # 장르 삭제 요청 리스트
                    genre_delete_list = genre_delete.split(',')
                    for genre_id in genre_delete_list:
                        # 장르 삭제
                        video.genre_list.get(id=genre_id).delete()
                except Exception as e:
                    raise Exception(e)
            # 비디오 상세 페이지로 리다이렉트
            return HttpResponseRedirect(reverse('content:video-detail', kwargs={'pk': video_id}))
        elif edit_type == "actor":
            actor_create = request.POST.get('actor_create')
            actor_delete = request.POST.get('actor_delete')
            # 배우정보 생성 요청 확인
            if actor_create:
                # 배우정보 생성요청 리스트
                actor_create_list = actor_create.split(',')
                for actor_id in actor_create_list:
                    try:
                        # 배우정보 가져오기
                        actor_type = request.POST.get('actor_type_' + actor_id)
                        actor_role = request.POST.get('actor_role_' + actor_id)
                        actor_name = request.POST.get('actor_name_' + actor_id)
                        # 배우가 이미 존재하는지 확인하고, 없으면 새로 생성
                        new_actor, created = Actor.objects.get_or_create(name=actor_name)
                        # 비디오에 배우정보 추가
                        video.actor_list.create(
                            type=actor_type,
                            role=actor_role,
                            actor=new_actor
                        )
                    except Exception as e:
                        raise Exception(e)
            # 배우정보 삭제 요청 확인
            if actor_delete:
                try:
                    # 배우정보 삭제요청 리스트
                    actor_delete_list = actor_delete.split(',')
                    for actor_id in actor_delete_list:
                        # 배우정보 삭제
                        actor = video.actor_list.get(id=actor_id)
                        actor.delete()
                except Exception as e:
                    raise Exception(e)
            # 배우정보 수정
            for actor in video.actor_list.all():
                try:
                    # 최종적으로 업데이트 여부 결정
                    is_update = False
                    # 배우정보 수정 요청 확인
                    actor_type = request.POST.get('actor_type_' + str(actor.id))
                    actor_name = request.POST.get('actor_name_' + str(actor.id))
                    actor_role = request.POST.get('actor_role_' + str(actor.id))
                    # 배우정보가 없으면 다음 배우정보로 이동
                    if actor_type is None or actor_name is None or actor_role is None:
                        continue
                    # 배우 이름이 변경된 경우
                    if actor.actor.name != actor_name:
                        # 배우정보 가져오기
                        get_actor = Actor.objects.filter(name=actor_name)
                        # 기존 DB에 배우정보가 있다면 첫번째 배우정보 가져옴
                        if get_actor:
                            actor.actor = get_actor[0]
                        # 없다면 신규 배우정보 생성
                        else:
                            new_actor = Actor(name=actor_name).save()
                            actor.actor = new_actor
                        # 업데이트 True로 변경
                        is_update = True
                    # 배우 타입 수정
                    if actor.type != actor_type:
                        actor.type = actor_type
                        # 업데이트 True로 변경
                        is_update = True
                    # 배우 역할 수정
                    if actor.role != actor_role:
                        actor.role = actor_role
                        # 업데이트 True로 변경
                        is_update = True
                    # 업데이트가 필요한 경우 저장
                    if is_update:
                        actor.save()
                except Exception as e:
                    raise Exception(e)
            # 비디오 상세 페이지로 리다이렉트
            return HttpResponseRedirect(reverse('content:video-detail', kwargs={'pk': video_id}))
        elif edit_type == "staff":
            staff_create = request.POST.get('staff_create')
            staff_delete = request.POST.get('staff_delete')
            # 시청정보 생성 요청 확인
            if staff_create:
                # 생성요청 시청정보 리스트
                staff_create_list = staff_create.split(',')
                for staff_id in staff_create_list:
                    try:
                        # 시청정보 가져오기
                        staff_type = request.POST.get('staff_type_' + staff_id)
                        staff_url = request.POST.get('staff_name_' + staff_id)
                        staff = video.staff.create(
                            type=staff_type,
                            url=staff_url
                        )
                        staff.save()
                    except Exception as e:
                        print(e)
            # 시청정보 삭제 요청 확인
            if staff_delete:
                # 삭제요청 시청정보 리스트
                staff_delete_list = staff_delete.split(',')
                for staff_id in staff_delete_list:
                    # 시청정보 삭제
                    staff = video.staff.get(id=staff_id)
                    staff.delete()
            # 비디오 상세 페이지로 리다이렉트
            return HttpResponseRedirect(reverse('content:video-detail', kwargs={'pk': video_id}))
        else:
            return render(request, self.template_name)


class GenreList(LoginRequiredMixin, ListView):
    login_url = DJANGO_LOGIN_URL
    redirect_field_name = DJANGO_REDIRECT_FIELD_NAME
    model = Genre
    template_name = "pages/content/genre/list.html"


class ActorList(LoginRequiredMixin, ListView):
    login_url = DJANGO_LOGIN_URL
    redirect_field_name = DJANGO_REDIRECT_FIELD_NAME
    model = Actor
    template_name = "pages/content/actor/list.html"


class StaffList(LoginRequiredMixin, ListView):
    login_url = DJANGO_LOGIN_URL
    redirect_field_name = DJANGO_REDIRECT_FIELD_NAME
    model = Staff
    template_name = "pages/content/staff/list.html"
