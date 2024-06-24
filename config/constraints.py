NETFLIX_LOGIN_URL = "https://www.netflix.com/login"
NETFLIX_CONTENT_URL = "https://www.netflix.com/kr/title/"
NETFLIX_BOXOFFICE_URL = "https://www.netflix.com/browse"

TVING_LOGIN_URL = "https://user.tving.com/pc/user/otherLogin.tving?loginType=10&from=pc"
TVING_CONTENT_URL = "https://www.tving.com/contents/"
TVING_BOXOFFICE_URL = "https://www.tving.com/boxoffice"

AWS_S3_VIDEO_THUMBNAIL = "video/thumbnail/"
AWS_S3_NETFLIX_THUMBNAIL = AWS_S3_VIDEO_THUMBNAIL + "netflix/"

AWS_S3_PATH_VIDEO_ACTOR = "video/actor/"

LOCAL_DATA_PATH = "data/"
LOCAL_NETFLIX_THUMBNAIL = LOCAL_DATA_PATH + AWS_S3_NETFLIX_THUMBNAIL

VIDEO_TYPE = [
    ('10', '영화'),
    ('11', '시리즈'),
]

VIDEO_PLATFORM_CODE = [
    ('10', '넷플릭스'),
    ('11', '디즈니플러스'),
    ('12', '티빙'),
    ('13', '웨이브'),
    ('14', '쿠팡플레이'),
    ('15', '왓챠'),
    ('50', '극장'),
]

VIDEO_THUMBNAIL_TYPE = [
    ('10', '대표 이미지'),
    ('11', '스틸컷'),
]

VIDEO_ACTOR_TYPE = [
    ('10', '주연'),
    ('11', '조연'),
    ('12', '단역'),
    ('13', '출연'),
    ('14', '나레이션'),
    ('15', '특별출연'),
    ('16', '카메오'),
    ('17', '우정출연'),
    ('18', '성우'),
]

VIDEO_STAFF_TYPE = [
    ('10', '감독'),
    ('11', '작가'),
    ('12', '제작'),
    ('13', '프로듀서'),
    ('14', '연출'),
    ('15', '기획'),
    ('16', '각본'),
    ('17', '원작'),
    ('18', '음악'),
    ('19', '미술'),
    ('20', '촬영'),
    ('21', '편집'),
    ('22', '특수효과'),
    ('23', '의상'),
    ('24', '분장'),
    ('25', '조명'),
    ('26', '극본'),
]
