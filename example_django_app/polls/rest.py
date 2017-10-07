from rest_framework.serializers import ModelSerializer

from django_remote_queryset.viewset import DRQModelViewSet
from polls.models import Poll


class PollModelSerializer(ModelSerializer):
    class Meta:
        model = Poll
        fields = ('id', 'title',)


class PollModelViewSet(DRQModelViewSet):
    queryset = Poll.objects.all()
    serializer_class = PollModelSerializer
