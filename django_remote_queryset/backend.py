import json
from base64 import b64decode

from django_remote_queryset.queries import QueryDecoder


class DRQFilterBackend(object):
    """
    
    """

    def drq_query_filter_queryset(self, json_query, qs):
        """
        
        :param json_query: 
        :param qs: 
        :return: 
        """
        filtered_queryset = qs

        query = QueryDecoder \
            .decodeJSONQuery(json_query)

        if query is not None:
            filtered_queryset = query.applyOnQuerySet(filtered_queryset)

        return filtered_queryset

    def filter_queryset(self, request, queryset, view):
        json_query = {}

        if 'query' in request.GET:
            json_query = json.loads(request.GET['query'])
        elif 'query_b64' in request.GET:
            json_query = json.loads(b64decode(request.GET['b64_query']))
        elif 'query' in request.data:
            json_query = request.data['query']

        filtered_queryset = self.drq_query_filter_queryset(json_query, qs=queryset)

        return filtered_queryset
