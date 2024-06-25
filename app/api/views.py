from rest_framework.response import Response
from rest_framework.views import APIView

from app.database.models import Actor, Staff
from app.utils.uploader import S3ImageUploader
from app.utils.utils import make_filename
from config.constraints import AWS_S3_PATH_VIDEO_ACTOR, AWS_S3_PATH_VIDEO_STAFF
from .serializers import ActorPictureUploadSerializer, StaffPictureUploadSerializer


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
                file_name = make_filename(file.name)
                print(file.name)
                print(file_name)
                s3_path = AWS_S3_PATH_VIDEO_ACTOR + actor_id + "/" + file_name
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
                file_name = make_filename(file.name)
                s3_path = AWS_S3_PATH_VIDEO_STAFF + staff_id + "/" + file_name
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
