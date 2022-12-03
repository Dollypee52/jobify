from news_app.models import Base, Comment, Poll, PollOption, Story
from rest_framework import serializers


class BaseSerializers(serializers.ModelSerializer):
    time = serializers.CharField(read_only=True)

    class Meta:
        model = Base
        # fields = "__all__"
        exclude = ["id"]


class CommentSerializers(serializers.ModelSerializer):
    time = serializers.CharField(read_only=True)

    class Meta:
        model = Comment
        fields = [
            "text",
            "story_id",
            "poll_id",
            "kids",
            "by",
            "time",
            "comment_comments",
        ]


class PollOptionSerializers(serializers.ModelSerializer):
    time = serializers.CharField(read_only=True)

    class Meta:
        model = PollOption
        fields = ["by", "url", "title", "text", "poll_id", "time"]