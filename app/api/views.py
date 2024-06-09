from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.database.models import (
    Video,
    VideoWatch,
    VideoThumbnail
)
from .serializers import (
    VideoWatchSerializer,
    VideoThumbnailSerializer,
    GenreSerializer
)


# Create your views here.
class Index(APIView):

    def get(self, request):
        return Response("Hello, world!")


class ApiVideoWatch(APIView):

    def get(self, request, video_id, watch_id=None):
        video = Video.objects.get(id=video_id)
        if not video:
            return Response("Video not found")
        watch = video.watch.all()
        serializer = VideoWatchSerializer(watch, many=True)
        return Response(serializer.data)

    def post(self, request, video_id):
        video_watch = request.data
        video_watch.update({"video": video_id})
        serializer = VideoWatchSerializer(data=video_watch)
        if not serializer.is_valid():
            return Response(serializer.errors)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, video_id, watch_id):
        video_watch = VideoWatch.objects.get(id=watch_id)
        video_watch.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, video_id, watch_id):
        video_watch = VideoWatch.objects.get(id=watch_id)
        if not video_watch:
            return Response("Watch data not found")
        video_watch_data = request.data
        serializer = VideoWatchSerializer(video_watch, data=video_watch_data)
        if not serializer.is_valid():
            return Response(serializer.errors)
        serializer.save()
        return Response(serializer.data)


class ApiVideoThumbnail(APIView):

    def get(self, request, video_id, thumbnail_id=None):
        video = Video.objects.get(id=video_id)
        if not video:
            return Response("Video not found")
        watch = video.thumbnail.all()
        serializer = VideoThumbnailSerializer(watch, many=True)
        return Response(serializer.data)

    def post(self, request, video_id):
        video_thumbnail = request.data
        video_thumbnail.update({"video": video_id})
        serializer = VideoThumbnailSerializer(data=video_thumbnail)
        if not serializer.is_valid():
            return Response(serializer.errors)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, video_id, thumbnail_id):
        video_thumbnail = VideoThumbnail.objects.get(id=thumbnail_id)
        video_thumbnail.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, video_id, thumbnail_id):
        video_thumbnail = VideoThumbnail.objects.get(id=thumbnail_id)
        if not video_thumbnail:
            return Response("Watch data not found")
        video_thumbnail_data = request.data
        serializer = VideoThumbnailSerializer(video_thumbnail, data=video_thumbnail_data)
        if not serializer.is_valid():
            return Response(serializer.errors)
        serializer.save()
        return Response(serializer.data)


class ApiVideoGenre(APIView):

    def get(self, request, video_id, thumbnail_id=None):
        video = Video.objects.get(id=video_id)
        if not video:
            return Response("Video not found")
        genre = video.genre.all()
        serializer = GenreSerializer(genre, many=True)
        return Response(serializer.data)

    def post(self, request, video_id):
        video_thumbnail = request.data
        video_thumbnail.update({"video": video_id})
        serializer = VideoThumbnailSerializer(data=video_thumbnail)
        if not serializer.is_valid():
            return Response(serializer.errors)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, video_id, thumbnail_id):
        video_thumbnail = VideoThumbnail.objects.get(id=thumbnail_id)
        video_thumbnail.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, video_id, thumbnail_id):
        video_thumbnail = VideoThumbnail.objects.get(id=thumbnail_id)
        if not video_thumbnail:
            return Response("Watch data not found")
        video_thumbnail_data = request.data
        serializer = VideoThumbnailSerializer(video_thumbnail, data=video_thumbnail_data)
        if not serializer.is_valid():
            return Response(serializer.errors)
        serializer.save()
        return Response(serializer.data)


class ApiVideoActor(APIView):

    def get(self, request, video_id, actor_id=None):
        pass

    def post(self, request, video_id):
        pass

    def delete(self, request, video_id, actor_id):
        pass

    def put(self, request, video_id, actor_id):
        pass


class ApiVideoStaff(APIView):

    def get(self, request, video_id, staff_id=None):
        pass

    def post(self, request, video_id):
        pass

    def delete(self, request, video_id, staff_id):
        pass

    def put(self, request, video_id, staff_id):
        pass
