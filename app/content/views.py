import os

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView, ListView, DetailView

from app.database.models import Video, Genre, Actor, Staff
from app.utils.s3client import S3Client
from app.utils.utils import make_filename, save_file_from_url, get_file_extension, get_file_size
from config.properties import (
    AWS_S3_NETFLIX_THUMBNAIL,
    LOCAL_NETFLIX_THUMBNAIL,
    THUMBNAIL_BASE_URL
)

DJANGO_LOGIN_URL = "/login/"
DJANGO_REDIRECT_FIELD_NAME = "next"


# Create your views here.
class Index(LoginRequiredMixin, TemplateView):
    login_url = DJANGO_LOGIN_URL
    redirect_field_name = DJANGO_REDIRECT_FIELD_NAME
    template_name = "pages/content/index.html"


class VideoList(LoginRequiredMixin, ListView):
    login_url = DJANGO_LOGIN_URL
    redirect_field_name = DJANGO_REDIRECT_FIELD_NAME
    model = Video
    template_name = "pages/content/video/list.html"
    context_object_name = "videos"

    def get_queryset(self):
        return Video.objects.order_by('-created_at').all()

    def set_thumbnail_urls_and_orientation(self, videos):
        for video in videos:
            video.is_vertical = False
            for thumbnail in video.thumbnail.all():
                thumbnail.url = THUMBNAIL_BASE_URL + thumbnail.url
                if thumbnail.type == "10":
                    video.is_vertical = True
        return videos

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        videos = self.set_thumbnail_urls_and_orientation(context['videos'])
        context['videos'] = videos
        return context


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
                # S3 클라이언트 생성
                s3client = S3Client()
                # 생성요청 썸네일 리스트 Loop
                for thumbnail_id in thumbnail_create_list:
                    # 썸네일 정보 가져오기
                    thumbnail_type = request.POST.get('thumbnail_type_' + thumbnail_id)
                    thumbnail_url = request.POST.get('thumbnail_' + thumbnail_id)
                    try:
                        # 썸네일 저장
                        file_name = make_filename(thumbnail_url)
                        file_path = os.path.join(LOCAL_NETFLIX_THUMBNAIL, file_name)
                        print(file_path)
                        if not save_file_from_url(thumbnail_url, file_path):
                            continue
                        # 썸네일 S3 업로드
                        if not s3client.upload_file(file_path, AWS_S3_NETFLIX_THUMBNAIL):
                            continue
                        # S3 업로드 성공 시 DB에 썸네일 정보 저장
                        thumbnail_url = os.path.join(AWS_S3_NETFLIX_THUMBNAIL, file_name)
                        thumbnail_extension = get_file_extension(file_name)
                        thumbnail_size = get_file_size(file_path)
                        thumbnail = video.thumbnail.create(
                            type=thumbnail_type,
                            url=thumbnail_url,
                            extension=thumbnail_extension,
                            size=thumbnail_size
                        )
                        thumbnail.save()
                    except Exception as e:
                        print(e)
                # S3 클라이언트 종료
                s3client.close()
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
