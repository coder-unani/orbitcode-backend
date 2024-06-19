import os
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
            # 파일 오픈
            with open(file_path, 'rb') as image_file:
                # Pillow 사용하여 이미지 가져옴
                with Image.open(image_file) as image:
                    image_format = image.format
                    image_width, image_height = image.size
                    # Reset the buffer's current position to the beginning
                    image_file.seek(0)
                    image_filename = f"{uuid.uuid4()}.{image_format.lower()}"
                    # S3에 이미지 업로드
                    if not self.upload(image_file, s3_path + image_filename):
                        return None
            # 이미지 정보 리턴
            return {
                "url": s3_path,
                "extension": image_format,
                "width": image_width,
                "height": image_height,
                "size": os.path.getsize(file_path)
            }
            # 이미지 파일명, 확장자, 사이즈 리턴
        except Exception as e:
            print(f"Failed to process the image: {e}")
            return None

    # 이미지 URL에서 이미지 다운로드 후 S3 업로드
    def upload_from_url(self, image_url, s3_path):
        try:
            # 이미지URL에서 다운로드
            response = requests.get(image_url)
            response.raise_for_status()
            response = requests.get(image_url)
            # Ensure we handle HTTP errors
            # 이미지 데이터 가져오기
            with BytesIO(response.content) as image_data:
                # 이미지 사이즈, 확장자 가져오기
                with Image.open(image_data) as image:
                    image_format = image.format
                    image_width, image_height = image.size
                # Reset the buffer's current position to the beginning
                image_size = len(response.content)
                image_data.seek(0)
                # S3에 이미지 업로드
                self.upload(image_data, s3_path)
                # 이미지 확장자, 사이즈 리턴
                return {
                    "url": s3_path,
                    "extension": image_format,
                    "width": image_width,
                    "height": image_height,
                    "size": image_size
                }
        except Exception as e:
            print(f"Failed to process the image: {e}")
            return None
    # 이미지 S3 업로드
    def upload(self, image, s3_path):
        try:
            print(image)
            print(s3_path)
            print(self.bucket)
            self.uploader.upload_fileobj(image, self.bucket, s3_path)
            print(f"Image uploaded to {self.bucket}/{s3_path}")
        except Exception as e:
            print(f"Failed to upload the image to S3: {e}")
            raise e
    # S3 클라이언트 종료
    def close(self):
        self.uploader.close()
