from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView
from app.database.models import Video, Genre, Actor, Staff

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

    def get_queryset(self):
        return Video.objects.order_by('-created_at')


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
        if edit_type == 'basic':
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
        elif edit_type == 'genre':
            pass
        elif edit_type == 'actor':
            pass
        elif edit_type == 'staff':
            pass
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
