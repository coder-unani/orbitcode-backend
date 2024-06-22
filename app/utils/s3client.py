
import boto3
from botocore.exceptions import ClientError
from django.conf import settings


class S3Client:
    def __init__(self, region=None):
        self._region = region
        if self._region is None:
            self._region = getattr(settings, "AWS_REGION")
        self._aws_access_key_id = getattr(settings, "AWS_ACCESS_KEY_ID")
        self._aws_secret_access_key = getattr(settings, "AWS_SECRET_ACCESS_KEY")
        self._aws_bucket_name = getattr(settings, "AWS_BUCKET_NAME")

        self._client = boto3.client(
            's3',
            aws_access_key_id=self._aws_access_key_id,
            aws_secret_access_key=self._aws_secret_access_key,
            region_name=self._region
        )

    def upload_file(self, file_path, destination):
        file_name = file_path.split('/')[-1]
        destination = destination + file_name
        try:
            self._client.upload_file(file_path, self._aws_bucket_name, destination)
            return destination
        except ClientError as e:
            print(e)
            return False

    def create_presigned_url(self, object_name, expiration=3600):
        try:
            response = self._client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self._aws_bucket_name,
                    'Key': object_name
                },
                ExpiresIn=expiration
            )
            return response
        except ClientError as e:
            print(e)
            return None

    def close(self):
        self._client.close()
