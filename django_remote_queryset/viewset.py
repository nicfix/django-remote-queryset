from rest_framework.viewsets import ModelViewSet

from django_remote_queryset.backend import DRQFilterBackend


class DRQModelViewSet(ModelViewSet):
    filter_backends = (DRQFilterBackend,)