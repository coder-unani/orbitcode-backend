import datetime

from django.db.models import Count
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from app.database.models import Video, Actor, Staff, User, VideoReview, VideoRating, VideoViewLog

DJANGO_LOGIN_URL = "/login/"
DJANGO_REDIRECT_FIELD_NAME = "next"


# Create your views here.
class Dashboard(LoginRequiredMixin, TemplateView):
    login_url = DJANGO_LOGIN_URL
    redirect_field_name = DJANGO_REDIRECT_FIELD_NAME
    template_name = "pages/dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['total_video'] = Video.objects.count()
        context['total_video_confirm_false'] = Video.objects.filter(is_confirm=False).count()
        context['total_actor'] = Actor.objects.count()
        context['total_staff'] = Staff.objects.count()
        context['total_user'] = User.objects.count()
        context['total_review'] = VideoReview.objects.count()
        context['total_rating'] = VideoRating.objects.count()
        context['total_video_read'] = VideoViewLog.objects.count()
        context['today_video_read'] = VideoViewLog.objects.filter(created_at__date=datetime.date.today()).count()
        context['total_write_review'] = VideoReview.objects.count()
        context['today_write_review'] = VideoReview.objects.filter(created_at__date=datetime.date.today()).count()

        actor = Actor.objects.values('name').annotate(name_count=Count('name')).filter(name_count__gt=1).order_by('-name_count')
        context['duplicated_actor'] = actor

        return context
