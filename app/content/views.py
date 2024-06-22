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
        queryset = super().get_queryset()
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
        context['video_platform'] = VIDEO_PLATFORM_CHOICES
        context['video_type'] = VIDEO_TYPE_CHOICES
        context['video_thumbnail_type'] = VIDEO_THUMBNAIL_TYPE
        context['video_actor_type'] = VIDEO_ACTOR_TYPE
        context['video_staff_type'] = VIDEO_STAFF_TYPE

        return context

    def post(self, request, *args, **kwargs):
        edit_type = request.POST.get('edit_type')
        if edit_type == "basic":
            video_id = kwargs.get('pk')
            video = Video.objects.get(id=video_id)
            if not video:
                print('video not found')
                return render(request, self.template_name)
            title = request.POST.get('title')
            if title:
                video.title = title
            type = request.POST.get('type')
            if type:
                video.type = type
            release = request.POST.get('release')
            if release:
                video.release = release
            runtime = request.POST.get('runtime')
            if runtime:
                video.runtime = runtime
            notice_age = request.POST.get('notice_age')
            if notice_age:
                video.notice_age = notice_age
            is_confirm = request.POST.get('is_confirm')
            if is_confirm:
                video.is_confirm = is_confirm == "true"
            video.save()
            return HttpResponseRedirect(reverse('content:video-detail', kwargs={'pk': video_id}))
        elif edit_type == "thumbnail":
            video_id = kwargs.get('pk')
            video = Video.objects.get(id=video_id)
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
                    thumbnail_url = request.POST.get('thumbnail_' + thumbnail_id)
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
            return HttpResponseRedirect(reverse('content:video-detail', kwargs={'pk': video_id}))
        elif edit_type == "watch":
            video_id = kwargs.get('pk')
            video = Video.objects.get(id=video_id)
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
                        watch_url = request.POST.get('watch_' + watch_id)
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
            return HttpResponseRedirect(reverse('content:video-detail', kwargs={'pk': video_id}))
        elif edit_type == "genre":
            video_id = kwargs.get('pk')
            video = Video.objects.get(id=video_id)
            genre_create = request.POST.get('genre_create')
            genre_delete = request.POST.get('genre_delete')
            # 시청정보 생성 요청 확인
            if genre_create:
                # 생성요청 시청정보 리스트
                genre_create_list = genre_create.split(',')
                for genre_id in genre_create_list:
                    try:
                        # 시청정보 가져오기
                        genre_type = request.POST.get('genre_type_' + genre_id)
                        genre_name = request.POST.get('genre_' + genre_id)
                        genre = video.genre.create(
                            type=genre_type,
                            url=genre_name
                        )
                        genre.save()
                    except Exception as e:
                        print(e)
            # 시청정보 삭제 요청 확인
            if genre_delete:
                # 삭제요청 시청정보 리스트
                genre_delete_list = genre_delete.split(',')
                for genre_id in genre_delete_list:
                    # 시청정보 삭제
                    genre = video.genre.get(id=genre_id)
                    genre.delete()
            return HttpResponseRedirect(reverse('content:video-detail', kwargs={'pk': video_id}))
        elif edit_type == "actor":
            video_id = kwargs.get('pk')
            video = Video.objects.get(id=video_id)
            actor_create = request.POST.get('actor_create')
            actor_delete = request.POST.get('actor_delete')
            # 시청정보 생성 요청 확인
            if actor_create:
                # 생성요청 시청정보 리스트
                actor_create_list = actor_create.split(',')
                for actor_id in actor_create_list:
                    try:
                        # 시청정보 가져오기
                        actor_type = request.POST.get('actor_type_' + actor_id)
                        actor_name = request.POST.get('actor_' + actor_id)
                        actor = video.actor.create(
                            type=actor_type,
                            url=actor_name
                        )
                        actor.save()
                    except Exception as e:
                        print(e)
            # 시청정보 삭제 요청 확인
            if actor_delete:
                # 삭제요청 시청정보 리스트
                actor_delete_list = actor_delete.split(',')
                for actor_id in actor_delete_list:
                    # 시청정보 삭제
                    actor = video.actor.get(id=actor_id)
                    actor.delete()
            return HttpResponseRedirect(reverse('content:video-detail', kwargs={'pk': video_id}))
        elif edit_type == "staff":
            video_id = kwargs.get('pk')
            video = Video.objects.get(id=video_id)
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
                        staff_url = request.POST.get('staff_' + staff_id)
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
