import json

from django.contrib.gis.geos import GEOSGeometry
from django.db.models import F, Q


class Query():
    def __init__(self, json_query):
        """
        Initializes the sub_tree of this query starting from the json_query parameter
        :param json_query: dict
        """
        pass

    def applyOnQuerySet(self, queryset):
        """
        Applies the sub_tree of this query to the queryset passed as parameter
        :param queryset: Queryset
        :return: Queryset
        """
        return queryset


class CompositeQuery(Query):
    order_by = None

    def __init__(self, json_query):
        self._sub_queries = []
        for query in json_query['_sub_queries']:
            if QueryDecoder.decodeJSONQuery(query):
                self._sub_queries.append(QueryDecoder.decodeJSONQuery(query))

    def applyOnQuerySet(self, queryset):
        for query in self._sub_queries:
            queryset = query.applyOnQuerySet(queryset)
        return queryset

    def get_sub_queries(self):
        return self._sub_queries


class OrQuery(CompositeQuery):
    def applyOnQuerySet(self, queryset):
        qs = queryset.none()

        for query in self._sub_queries:
            if isinstance(query, CompositeQuery):
                # qs = CompoundQueryset(qs, query.applyOnQuerySet(queryset))
                qs = qs | query.applyOnQuerySet(queryset)

        for query in self._sub_queries:
            if not isinstance(query, CompositeQuery):
                qs = query.applyOnQuerySet(qs)


class All(Query):
    def __init__(self, json_query):
        pass

    def applyOnQuerySet(self, queryset):
        return queryset.all()


class Filter(Query):
    """
    Applies the .filter( ... ) method on the queryset
    """

    def __init__(self, json_query):
        """
        Builds the query,
        
        Syntax:
        
        json_query = {
            "_query_class":"filter",
            "_filter_condition": [string] | string,
            "_values": [*] | * 
        }
        
        :param json_query: dict
        """
        self.filter_condition = json_query['_condition']

        conditions = []
        values = []

        if isinstance(self.filter_condition, (list, tuple)):
            for cond in self.filter_condition:
                conditions.append(cond)
        else:
            conditions.append(self.filter_condition)

        try:
            value = GEOSGeometry(json.dumps(json_query['_value']))
        except Exception as e:
            value = json_query['_value']

        self.filter_value = value

        if isinstance(self.filter_condition, (list, tuple)):
            if isinstance(self.filter_value, (list, tuple)):
                for v in self.filter_value:
                    values.append(v)

        else:
            values.append(self.filter_value)

        self.query = {}

        for idx, condition in enumerate(conditions):
            self.query[condition] = values[idx]

    def applyOnQuerySet(self, queryset):
        return queryset.filter(**self.query)


class OrderBy(Query):
    def __init__(self, json_query):
        self.order_by = json_query['_order_by']

    def applyOnQuerySet(self, queryset):
        queryset = queryset.order_by(*self.order_by)
        return queryset


class Exclude(Query):
    def __init__(self, json_query):
        self.filter_condition = json_query['_condition']

        conditions = []
        values = []

        if isinstance(self.filter_condition, (list, tuple)):
            for cond in self.filter_condition:
                conditions.append(cond)
        else:
            conditions.append(self.filter_condition)

        try:
            value = GEOSGeometry(json.dumps(json_query['_value']))
        except Exception as e:
            value = json_query['_value']

        self.filter_value = value

        if isinstance(self.filter_condition, (list, tuple)):
            if isinstance(self.filter_value, (list, tuple)):
                for v in self.filter_value:
                    values.append(v)

        else:
            values.append(self.filter_value)

        self.query = {}

        for idx, condition in enumerate(conditions):
            self.query[condition] = values[idx]

    def applyOnQuerySet(self, queryset):
        return queryset.exclude(**self.query)


class SelfFieldFilter(Filter):
    def __init__(self, json_query):
        self.filter_condition = json_query['_condition']

        self.inner_condition = json_query['_field_to_compare']

        self.query = {self.filter_condition: F(self.inner_condition)}


class SelfFieldExclude(Exclude):
    def __init__(self, json_query):
        self.filter_condition = json_query['_condition']

        self.inner_condition = json_query['_field_to_compare']

        self.query = {self.filter_condition: F(self.inner_condition)}


class QueryFilter(Filter):
    def __init__(self, json_query):
        self.filter_condition = json_query['_condition']

        self.inner_condition = json_query['_inner_condition']

        self.filter_value = json_query['_value']

        self.inner_query = {self.inner_condition: self.filter_value}

        self.query = {self.filter_condition: Q(**self.inner_query)}


class QueryExclude(Exclude):
    def __init__(self, json_query):
        self.filter_condition = json_query['_condition']

        self.inner_condition = json_query['_inner_condition']

        self.filter_value = json_query['_value']

        self.inner_query = {self.inner_condition: self.filter_value}

        self.query = {self.filter_condition: Q(**self.inner_query)}


class Distinct(Query):
    def applyOnQuerySet(self, queryset):
        return queryset.distinct()


class QueryDecoder():
    @staticmethod
    def decodeJSONQuery(json_query):
        query = None
        if json_query is not None:
            if '_query_class' in json_query:
                try:
                    query = DRQ_QUERY_GLOSSARY[str(json_query['_query_class'])](json_query)
                except:
                    query = None
        return query


DRQ_QUERY_GLOSSARY = {
    Query.__name__.lower(): Query,
    Filter.__name__.lower(): Filter,
    Exclude.__name__.lower(): Exclude,
    OrderBy.__name__.lower(): OrderBy,
    CompositeQuery.__name__.lower(): CompositeQuery,
    OrQuery.__name__.lower(): OrQuery,
    SelfFieldFilter.__name__.lower(): SelfFieldFilter,
    SelfFieldExclude.__name__.lower(): SelfFieldExclude,
    Distinct.__name__.lower(): Distinct
}
