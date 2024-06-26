import os
import uuid
from urllib.request import urlretrieve

from django.utils.html import escape

from config.constraints import AWS_S3_PATH_ACTOR, AWS_S3_PATH_STAFF, AWS_S3_PATH_VIDEO


def html_escape(text):
    return escape(text)


def make_s3_path(upload_type, key, file_name):
    # 업로드 타입이 actor, staff, video가 아니면 False 반환
    if upload_type not in ["actor", "staff", "video"]:
        return False
    # 파일명이나 키가 없으면 False 반환
    if not file_name or not key:
        return False
    # 기본 경로
    base_path = ""
    # 업로드 타입에 따라 기본 경로 설정
    if upload_type == "actor":
        base_path = AWS_S3_PATH_ACTOR
    if upload_type == "staff":
        base_path = AWS_S3_PATH_STAFF
    if upload_type == "video":
        base_path = AWS_S3_PATH_VIDEO
    # 기본 경로 끝이 /로 끝나지 않으면 /를 추가
    if not base_path.endswith("/"):
        base_path = f"{base_path}/"
    # 기본 경로에 키 값 추가
    base_path = f"{base_path}{key}/"
    # 파일명에서 확장자 추출
    file_ext = file_name.split(".")[-1]
    # 확장자에서 파라메터 제거
    file_ext = file_ext.split("?")[0]
    file_ext = file_ext.split("/")[0]
    # 확장자 소문자 변환
    file_ext = file_ext.lower()
    # 파일명
    file_name = f"{uuid.uuid4()}.{file_ext}"
    # S3 경로 반환
    return f"{base_path}{file_name}"


def save_file_from_url(file, file_path):
    try:
        urlretrieve(file, file_path)
        return True
    except Exception as e:
        print(e)
        return False


def get_file_extension(file_name):
    return file_name.split(".")[-1].lower()


def get_file_size(file):
    if os.path.isfile(file):
        return os.path.getsize(file)
    else:
        return None
