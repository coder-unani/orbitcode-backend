from rest_framework import serializers


class ActorPictureUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    actor_id = serializers.CharField()


class StaffPictureUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    staff_id = serializers.CharField()