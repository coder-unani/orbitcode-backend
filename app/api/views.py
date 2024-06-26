from PIL import Image
from rest_framework.response import Response
from rest_framework.views import APIView

from app.database.models import Actor, Staff
from app.utils.uploader import S3ImageUploader
from app.utils.utils import make_s3_path
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


# class VideoThumbnailUploadPre(APIView):
#
#     def post(self, request, *args, **kwargs):
#         serializer = VideoThumbnailUploadSerializer(data=request.data)
#         if serializer.is_valid():
#             try:
#                 file = serializer.validated_data['file']
#                 video_id = serializer.validated_data['video_id']
#                 s3_path = make_s3_path("video", video_id, file.name)
#                 size = 300
#                 with Image.open(file) as image:
#                     image_format = image.format
#                     image_width, image_height = image.size
#                     aspect_ratio = image.height / image.width
#                     if image.width >= image.height:  # 가로 이미지
#                         width = size
#                         height = int(size * aspect_ratio)
#                     else:  # 세로 이미지
#                         height = size
#                         width = int(size / aspect_ratio)
#                     image.resize((width, height), Image.Resampling.LANCZOS)
#                     image_width, image_height = image.size
#
#                 return Response({
#                     "url": s3_path,
#                     "extension": image_format,
#                     "width": image_width,
#                     "height": image_height,
#                     "size": len(file.read())
#                 }, status=200)
#
#                 if result is None:
#                     return Response("Failed to upload the image", status=400)
#                 return Response(result, status=200)
#             except Exception as e:
#                 print(e)
#                 return Response("Failed to upload the image", status=400)
#         else:
#             return Response("Failed to upload the image", status=400)