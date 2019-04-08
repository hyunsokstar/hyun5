from rest_framework import serializers
from .import models
from nomadgram.users import models as user_models
from taggit_serializer.serializers import (TagListSerializerField, TaggitSerializer)

# 시리얼라이저 추가
class InputImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Image
        fields = (
            'file',
            'location',
            'caption',
        )

class SmallImageSerializer(serializers.ModelSerializer):
    """ Used for the notifications """
    class Meta:
        model = models.Image
        fields = (
            'file',
        )

# class UserProfileImageSerializer(serializers.ModelSerializer):
class CountImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Image
        fields = (
            'id',
            'file',
            'like_count',
            'comment_count',
        )

class FeedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_models.User
        fields = (
            'username',
            'profile_image'
        )

class CommentSerializer(serializers.ModelSerializer):
    # creator = FeedUserSerializer()
    creator = FeedUserSerializer(read_only=True)

    class Meta:
        model = models.Comment
        fields = (
            'id',
            'message',
            'creator',
        )

class LikeSerializer(serializers.ModelSerializer):
    # image = ImageSerializer()
    class Meta:
        model = models.Like
        fields = '__all__'


class ImageSerializer(serializers.ModelSerializer):
    creator = FeedUserSerializer()
    comments = CommentSerializer(many=True)
    tags = TagListSerializerField()

    class Meta:
        model = models.Image
        fields = (
            'id',
            'file',
            'location',
            'caption',
            'comments',
            'like_count',
            'creator',
            'comment_count',
            'tags',
        )
