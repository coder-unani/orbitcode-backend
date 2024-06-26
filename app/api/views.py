from rest_framework.response import Response
from rest_framework.views import APIView

from app.database.models import Actor, Staff, Genre
from app.utils.uploader import S3ImageUploader
from app.utils.utils import make_s3_path
from config.settings.settings import AWS_S3_BASE_URL
from .serializers import VideoThumbnailUploadSerializer, ActorPictureUploadSerializer, StaffPictureUploadSerializer


# Create your views here.
class Index(APIView):

    def get(self, request):
        return Response("Hello, world!")


class ActorPictureUpload(APIView):

    def post(self, request, *args, **kwargs):
        serializer = ActorPictureUploadSerializer(data=request.data)
        if serializer.is_valid():
            try:
                file = serializer.validated_data['file']
                actor_id = serializer.validated_data['actor_id']
                s3_path = make_s3_path("actor", actor_id, file.name)
                uploader = S3ImageUploader()
                result = uploader.upload_from_file(file, s3_path, 300)
                uploader.close()
                if result is None:
                    return Response("Failed to upload the image", status=400)
                Actor.objects.filter(id=actor_id).update(picture=result['url'])
                return Response(result, status=200)
            except Exception as e:
                print(e)
                return Response("Failed to upload the image", status=400)
        else:
            return Response("Failed to upload the image", status=400)


class StaffPictureUpload(APIView):

    def post(self, request, *args, **kwargs):
        serializer = StaffPictureUploadSerializer(data=request.data)
        if serializer.is_valid():
            try:
                file = serializer.validated_data['file']
                staff_id = serializer.validated_data['staff_id']
                s3_path = make_s3_path("staff", staff_id, file.name)
                uploader = S3ImageUploader()
                result = uploader.upload_from_file(file, s3_path, 300)
                uploader.close()
                if result is None:
                    return Response("Failed to upload the image", status=400)
                Staff.objects.filter(id=staff_id).update(picture=result['url'])
                return Response(result, status=200)
            except Exception as e:
                print(e)
                return Response("Failed to upload the image", status=400)
        else:
            return Response("Failed to upload the image", status=400)


class VideoThumbnailUpload(APIView):

    def post(self, request, *args, **kwargs):
        serializer = VideoThumbnailUploadSerializer(data=request.data)
        if serializer.is_valid():
            try:
                file = serializer.validated_data['file']
                video_id = serializer.validated_data['video_id']
                s3_path = make_s3_path("video", video_id, file.name)
                uploader = S3ImageUploader()
                result = uploader.upload_from_file(file, s3_path, 300)
                uploader.close()
                if result is None:
                    return Response("Failed to upload the image", status=400)
                return Response(result, status=200)
            except Exception as e:
                print(e)
                return Response("Failed to upload the image", status=400)


class FindActor(APIView):

    def get(self, request, *args, **kwargs):
        name = request.query_params.get('q', None)
        if not name:
            return Response("Failed to find the actor", status=400)
        actors = Actor.objects.filter(name__contains=name).values('id', 'name', 'picture')
        for actor in actors:
            actor['picture'] = f"{AWS_S3_BASE_URL}{actor['picture']}" if actor['picture'] else "/static/images/no-people.png"
        return Response(actors, status=200)


class FindStaff(APIView):

    def get(self, request, *args, **kwargs):
        name = request.query_params.get('q', None)
        if not name:
            return Response("Failed to find the actor", status=400)
        staffs = Staff.objects.filter(name__contains=name).values('id', 'name', 'picture')
        for staff in staffs:
            staff['picture'] = f"{AWS_S3_BASE_URL}{staff['picture']}" if staff['picture'] else "/static/images/no-people.png"
        return Response(staffs, status=200)


class FindGenre(APIView):

    def get(self, request, *args, **kwargs):
        name = request.query_params.get('q', None)
        if not name:
            return Response("Failed to find the actor", status=400)
        genres = Genre.objects.filter(name__contains=name).values('id', 'name')
        return Response(genres, status=200)
