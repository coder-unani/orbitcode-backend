import uuid
from abc import ABC, abstractmethod
from io import BytesIO

import boto3
import requests
from PIL import Image
from django.conf import settings


class ImageUploader(ABC):
    @abstractmethod
    def upload_from_file(self, file_path, s3_path):
        pass

    @abstractmethod
    def upload_from_url(self, image_url, s3_path):
        pass

    @abstractmethod
    def close(self):
        pass


class S3ImageUploader(ImageUploader):
    def __init__(
        self,
        uploader=None,
        region=settings.AWS_REGION,
        bucket=settings.AWS_BUCKET_NAME,
        access_key_id=settings.AWS_ACCESS_KEY_ID,
        secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    ):
        # S3 Client 생성
        if uploader is None:
            self.uploader = boto3.client(
                's3',
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
                region_name=region
            )
        else:
            self.uploader = uploader
        # S3 Bucket 설정
        self.bucket = bucket
    # 파일 경로에서 이미지 다운로드 후 S3 업로드
    def upload_from_file(self, file_path, s3_path):
        try:
            # Open the image file
            with open(file_path, 'rb') as image_file:
                # Get the image format and size using Pillow
                with Image.open(image_file) as image:
                    image_format = image.format
                    image_size = image.size
                # Reset the buffer's current position to the beginning
                image_file.seek(0)
                image_filename = f"{uuid.uuid4()}.{image_format.lower()}"
                # S3에 이미지 업로드
                self.upload(image_file, s3_path + image_filename)
            # 이미지 파일명, 확장자, 사이즈 리턴
            return {
                "name": s3_path + image_filename,
                "extension": image_format,
                "size": image_size
            }
        except requests.exceptions.RequestException as e:
            print(f"Failed to download the image: {e}")
            return None, None
        except Exception as e:
            print(f"Failed to upload the image to S3: {e}")
            raise e
    # 이미지 URL에서 이미지 다운로드 후 S3 업로드
    def upload_from_url(self, image_url, s3_path):
        try:
            # 이미지URL에서 다운로드
            response = requests.get(image_url)
            response.raise_for_status()  # Ensure we handle HTTP errors
            # 이미지 데이터 가져오기
            with BytesIO(response.content) as image_data:
                # 이미지 사이즈, 확장자 가져오기
                with Image.open(image_data) as image:
                    image_format = image.format
                    image_size = image.size
                # Reset the buffer's current position to the beginning
                image_data.seek(0)
                image_filename = f"{uuid.uuid4()}.{image_format.lower()}"
            # S3에 이미지 업로드
            self.upload(image_data, s3_path + image_filename)
            # 이미지 확장자, 사이즈 리턴
            return image_format, image_size
        except requests.exceptions.RequestException as e:
            print(f"Failed to download the image: {e}")
            return None, None
        except Exception as e:
            print(f"Failed to process the image: {e}")
            return None, None
    # 이미지 S3 업로드
    def upload(self, image, s3_path):
        try:
            self.uploader.upload_fileobj(image, self.bucket, s3_path)
            print(f"Image uploaded to {self.bucket}/{s3_path}")
        except self.uploader.exceptions.S3UploadFailedError as e:
            print(f"Failed to upload the image to S3: {e}")
            raise e
    # S3 클라이언트 종료
    def close(self):
        self.uploader.close()
