from django.shortcuts import get_object_or_404
from news_app.models import Base, Comment, Job, Poll, PollOption, Story
from rest_framework import status, viewsets, filters
from rest_framework.response import Response

from .serializers import (BaseSerializers, CommentSerializers,
                          PollOptionSerializers)


def deletion(cls, pk, request):
    obj = get_object_or_404(cls, pk=pk)
    if obj.generated:
        return Response(
            "Deletions of fetched item not allowed",
            status=status.HTTP_403_FORBIDDEN,
        )
    obj.delete()
    return Response("Deleted successfully")


def updown(cls, clss, pk, request):
    obj = get_object_or_404(cls, pk=pk)
    if obj.generated:
        return Response(
            "Update of fetched item not allowed",
            status=status.HTTP_403_FORBIDDEN,
        )
    ser = clss(data=request.data)
    if ser.is_valid(raise_exception=True):
        ser.save()
        return Response(ser.data)


class BaseViewSet(viewsets.ModelViewSet):
    queryset = Base.objects.exclude(type__in=("comment", "pollopt"))
    serializer_class = BaseSerializers
    filter_backends = [filters.SearchFilter]
    search_fields = ['type']

    def list(self, request):
        type = request.GET.get("type")
        text = request.GET.get("text")
        generated = request.GET.get("generated")
        query_set = self.queryset
        if type and text and generated is not None:
            query_set = query_set.filter(
                text__icontains=text.lower(), type=type.lower(), fetched=generated
            )
        else:
            if generated != None:
                query_set = query_set.filter(fetched=generated)
            if type:
                query_set = query_set.filter(type=type.lower())
            if text:
                query_set = query_set.filter(text__icontains=text.lower())

        page = self.paginate_queryset(query_set)
        if page:
            data = BaseSerializers(page, many=True).data
            return self.get_paginated_response(data)
        data = BaseSerializers(query_set, many=True).data
        return Response(data)

    def create(self, request):
        ser = BaseSerializers(data=request.data)
        stor = {"job": Job, "story": Story, "poll": Poll}
        data = dict(request.data)
        if ser.is_valid(raise_exception=True):
            type = ser.data.get("type")
            score = int(data["score"][0])
            text = data["text"][0]
            by = data["by"][0]
            url = data["url"][0]
            del data["text"]
            del data["by"]
            del data["csrfmiddlewaretoken"]
            del data["score"]
            del data["url"]
            saved = stor[type].objects.create(
                **data, score=score, url=url, text=text, by=by
            )
            saved.obj_id = saved.id
            saved.save()
            return Response("Successfully created", status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        return deletion(Base, pk, request)

    def update(self, request, pk=None):
        return updown(Base, BaseSerializers, pk, request)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializers
    filter_backends = [filters.SearchFilter]
    search_fields = ['text']

    def destroy(self, request, pk=None):
        return deletion(Comment, pk, request)

    def update(self, request, pk=None):
        return updown(Comment, CommentSerializers, pk, request)


class PollOptionViewSet(viewsets.ModelViewSet):
    queryset = PollOption.objects.all()
    serializer_class = PollOptionSerializers

    def destroy(self, request, pk=None):
        return deletion(PollOption, pk, request)

    def update(self, request, pk=None):
        return updown(PollOption, PollOptionSerializers, pk, request)
