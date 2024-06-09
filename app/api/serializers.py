from rest_framework import serializers, viewsets

from app.database.models import (
    Video,
    VideoWatch,
    VideoThumbnail,
    VideoGenre,
    VideoActor,
    VideoStaff,
    Genre,
    Actor,
    Staff
)


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'


class VideoWatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoWatch
        fields = '__all__'


class VideoThumbnailSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoThumbnail
        fields = '__all__'


class VideoGenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoGenre
        fields = '__all__'


class VideoActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoActor
        fields = '__all__'


class VideoStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoStaff
        fields = '__all__'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = '__all__'


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = '__all__'


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

