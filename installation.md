python3 manage.py createsuperuser --username=orbitcode --email=groot@orbitcode.kr# 파이썬 가상환경 설치
~~~bash
python3 -m venv .venv
~~~

# 가상환경 활성화
~~~bash
source .venv/bin/activate
~~~

# Django 설치
~~~bash
pip install django==5.0
~~~

# 추가 패키지 설치
~~~bash
pip install django-environ
pip install psycopg2-binary
pip install djangorestframework
pip install uuid
pip install markdown
pip install django-filter
pip install boto3
pip install beautifulsoup4
pip install selenium

pip freeze > requirements.txt
~~~

# django 프로젝트 생성
~~~bash
django-admin startproject config .

# settings 파일 이동
config/settings.py -> config/settings/settings.py

# static, templates 폴더 생성
static/
templates/

# settings.py 설정 (settings.py 파일 참조)

# .env 파일 생성
.env.development
.env.production
~~~

# REST_FRAMEWORK 설정
~~~bash
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny'
    ]
}
~~~

# django 앱 생성
~~~bash
python manage.py startapp api
python manage.py startapp dashboard
python manage.py startapp builder
python manage.py startapp content
python manage.py startapp user
python manage.py startapp database
python manage.py startapp utils
~~~

# django 앱 경로 이동
~~~bash
# app 폴더 생성
app/
    api/
    dashboard/
    builder/
    content/
    user/
    database/
    utils/

# 각각의 앱 안의 apps.py 파일 수정
~~~
