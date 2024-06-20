from django.db import models
from django.utils import timezone


#=======================================================================================================================
# Video
class Video(models.Model):
    # 타입 : 10=movie, 11=series
    type = models.CharField(max_length=2, null=False, db_index=True)
    # 타이틀
    title = models.CharField(max_length=100, null=False, db_index=True)
    # 시놉시스
    synopsis = models.TextField(null=True)
    # 개봉년도
    release = models.CharField(max_length=20, null=True)
    # 상영시간
    runtime = models.CharField(max_length=20, null=True)
    # 연령고지
    notice_age = models.CharField(max_length=20, null=True)
    # 평점
    rating = models.FloatField(default=0.0, db_index=True)
    # 좋아요 수
    like_count = models.IntegerField(default=0)
    # 리뷰 수
    review_count = models.IntegerField(default=0)
    # 조회수
    view_count = models.IntegerField(default=0)
    # 플랫폼 코드: 10=netflix, 11=disney+, 12=tving, 13=waave, 14=coupang play, 15=watcha, 50=Theater
    platform_code = models.CharField(max_length=2, null=False, db_index=True)
    # 플랫폼별 ID
    platform_id = models.CharField(max_length=50, null=False)
    # 확인여부
    is_confirm = models.BooleanField(default=False)
    # 삭제여부
    is_delete = models.BooleanField(default=False)

    # 생성일, 수정일
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "rvvs_video"


class Actor(models.Model):
    # 배우이름
    name = models.CharField(max_length=100, null=False, db_index=True)
    # 배우사진
    picture = models.CharField(max_length=200, null=True)
    # 프로필
    profile = models.TextField(null=True)
    # 생성일, 수정일
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, auto_now=True)
    # ManyToManyField
    video = models.ManyToManyField(Video, through='VideoActor', related_name="actor")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "rvvs_actor"


class Staff(models.Model):
    # 이름
    name = models.CharField(max_length=100, null=False, db_index=True)
    # 프로필 이미지
    picture = models.CharField(max_length=200, null=True)
    # 프로필
    profile = models.TextField(null=True)
    # 생성일, 수정일
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, auto_now=True)
    # ManyToManyField
    video = models.ManyToManyField(Video, through='VideoStaff', related_name="staff")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "rvvs_staff"


class Genre(models.Model):
    # 장르
    name = models.CharField(max_length=50, null=False, db_index=True)
    # 생성일, 수정일
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, auto_now=True)
    # ManyToManyField
    video = models.ManyToManyField(Video, through='VideoGenre', related_name="genre")
    def __str__(self):
        return self.name

    class Meta:
        db_table = "rvvs_genre"


class VideoActor(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="actor_list")
    # 출연진
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE)
    # 타입 : 10=main actor, 11=sub actor
    type = models.CharField(max_length=2, null=False)
    # 역할
    role = models.CharField(max_length=100, null=True)
    # 생성일, 수정일
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, auto_now=True)

    def __str__(self):
        return self.actor

    class Meta:
        db_table = "rvvs_video_actor"


class VideoStaff(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="staff_list")
    # 스태프
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    # 타입 : 10=director, 11=creator
    type = models.CharField(max_length=2, null=False)
    # 생성일, 수정일
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, auto_now=True)

    def __str__(self):
        return self.staff

    class Meta:
        db_table = "rvvs_video_staff"


class VideoGenre(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="genre_list")
    # 장르
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    # 생성일, 수정일
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, auto_now=True)

    def __str__(self):
        return self.genre

    class Meta:
        db_table = "rvvs_video_genre"


class VideoThumbnail(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="thumbnail")
    # 타입 : 10=poster, 11=thumbnail
    type = models.CharField(max_length=2, null=False)
    # 썸네일 URL
    url = models.CharField(max_length=1000, null=False)
    # 확장자
    extension = models.CharField(max_length=10, null=False)
    # 사이즈
    size = models.BigIntegerField(null=True)
    width = models.IntegerField(null=True)
    height = models.IntegerField(null=True)
    # 생성일, 수정일
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, auto_now=True)

    def __str__(self):
        return self.url

    class Meta:
        db_table = "rvvs_video_thumbnail"
        ordering = ['type']


class VideoWatch(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="watch")
    # 타입: 10=main contents, 11=trailer
    type = models.CharField(max_length=2, null=False)
    # 시청 URL
    url = models.CharField(max_length=100, null=False)
    # 생성일, 수정일
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, auto_now=True)

    def __str__(self):
        return self.url

    class Meta:
        db_table = "rvvs_video_watch"


class VideoTag(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="tag")
    # 태그 이름
    name = models.CharField(max_length=50, null=False, db_index=True)
    # 생성일, 수정일
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "rvvs_video_tag"


class VideoRank(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="rank")
    # 타입 : 10=netflix, 11=disney+, 12=tving, 13=waave, 14=coupang play, 15=watcha, 50=Theater
    platform_code = models.CharField(max_length=2, null=False)
    # 기준 코드
    rank_code = models.CharField(max_length=20, null=False)
    # 랭킹 분류
    rank_type = models.CharField(max_length=2, null=False)
    # 랭킹
    rank = models.IntegerField(default=0)
    # 생성일
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.rank

    class Meta:
        db_table = "rvvs_video_rank"


#=======================================================================================================================
# User
class User(models.Model):
    # 타입 : 10 = email, 11 = google, 12 = facebook, 13 = apple, 14 = kakao, 15 = naver
    type = models.CharField(max_length=2, null=False)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=60)
    nickname = models.CharField(max_length=40, unique=True, null=True)
    profile_image = models.CharField(max_length=100, null=True)
    profile_text = models.TextField(null=True)
    birth_year = models.IntegerField(null=True)
    level = models.IntegerField(default=0)
    mileage = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    review_count = models.IntegerField(default=0)
    rating_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_block = models.BooleanField(default=False)
    is_email_verify = models.BooleanField(default=False)
    is_privacy_agree = models.BooleanField(default=False)
    is_terms_agree = models.BooleanField(default=False)
    is_age_agree = models.BooleanField(default=False)
    is_marketing_agree = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, auto_now=True)

    def __str__(self):
        return self.nickname

    class Meta:
        db_table = "rvvs_user"


# 사용자 취향 정의
class UserFavorite(models.Model):
    name = models.CharField(max_length=50, null=False)
    is_display = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "rvvs_user_favorite"


# 사용자 취향 리스트
class UserFavoriteList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorite")
    favorite = models.ForeignKey(UserFavorite, on_delete=models.CASCADE, related_name="user")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "rvvs_user_favorite_list"

#=======================================================================================================================
# Video Rating , Review, Like


# 비디오 평점
class VideoRating(models.Model):
    video_id = models.IntegerField(null=False, db_index=True)
    rating = models.IntegerField(default=0)
    user_id = models.IntegerField(null=False, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, auto_now=True)

    def __str__(self):
        return self.rating

    class Meta:
        db_table = "rvvs_video_rating"


# 비디오 좋아요
class VideoLike(models.Model):
    # 비디오 ID
    video_id = models.IntegerField(null=False, db_index=True)
    # 비디오 제목
    video_title = models.CharField(max_length=100, null=False)
    # 좋아요 타입
    like_type = models.CharField(max_length=2, null=False)
    # 좋아요 여부
    is_like = models.BooleanField(default=False)
    # 사용자 ID
    user_id = models.IntegerField(null=False, db_index=True)
    # 생성일
    created_at = models.DateTimeField(default=timezone.now)
    # 수정일
    updated_at = models.DateTimeField(null=True, auto_now=True)

    def __str__(self):
        return self.user_id

    class Meta:
        db_table = "rvvs_video_like"


# 비디오 리뷰
class VideoReview(models.Model):
    video_id = models.IntegerField(null=False, db_index=True)
    user_id = models.IntegerField(null=False, db_index=True)
    user_nickname = models.CharField(max_length=40, null=True)
    user_profile_image = models.CharField(max_length=100, null=True)
    title = models.CharField(max_length=200, null=False)
    content = models.TextField(null=True)
    like_count = models.IntegerField(default=0)
    is_spoiler = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    is_block = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "rvvs_video_review"


# 비디오 리뷰 좋아요
class VideoReviewLike(models.Model):
    review_id = models.IntegerField(null=False, db_index=True)
    user_id = models.IntegerField(null=False, db_index=True)
    is_like = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, auto_now=True)

    def __str__(self):
        return self.user_id

    class Meta:
        db_table = "rvvs_video_review_like"

#=======================================================================================================================
# Log


# 비디오 조회 로그
class VideoViewLog(models.Model):
    # 비디오 ID
    video_id = models.IntegerField(null=False, db_index=True)
    # 사용자 ID
    user_id = models.IntegerField(null=True, db_index=True)
    # client IP
    client_ip = models.CharField(max_length=50, null=True)
    # 생성일
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user_id

    class Meta:
        db_table = "rvvs_log_video_view"


# 사용자 로그인 로그
class UserLoginLog(models.Model):
    status = models.IntegerField(null=False)
    code = models.CharField(max_length=50, null=True)
    message = models.CharField(max_length=200, null=True)
    path = models.CharField(max_length=200, null=True)
    input_id = models.CharField(max_length=200, null=True)
    client_ip = models.CharField(max_length=50, null=True)
    client_host = models.CharField(max_length=200, null=True)
    user_agent = models.CharField(max_length=200, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "rvvs_log_user_login"
