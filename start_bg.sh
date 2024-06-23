#!/bin/bash

# Django 프로젝트 디렉토리로 이동
cd /data/app/orbitcode/galaxy

# 가상 환경 활성화
source /data/app/orbitcode/galaxy/.venv/bin/activate

# Gunicorn을 백그라운드에서 실행하고 로그를 파일에 저장
nohup gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 > gunicorn.log 2>&1 &