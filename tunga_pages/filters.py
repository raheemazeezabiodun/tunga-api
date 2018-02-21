# -*- coding: utf-8 -*-
import django_filters

from tunga_pages.models import BlogPost
from tunga_utils.filters import GenericDateFilterSet


class BlogPostFilter(GenericDateFilterSet):
    min_created_at = django_filters.IsoDateTimeFilter(name='created_at', lookup_expr='gte')
    max_created_at = django_filters.IsoDateTimeFilter(name='created_at', lookup_expr='lte')
    min_published_at = django_filters.IsoDateTimeFilter(name='published_at', lookup_expr='gte')
    max_published_at = django_filters.IsoDateTimeFilter(name='published_at', lookup_expr='lte')
    status = django_filters.CharFilter(method='filter_status')

    class Meta:
        model = BlogPost
        fields = (
            'created_by', 'published', 'status', 'min_created_at', 'max_created_at', 'min_published_at', 'max_published_at'
        )

    def filter_status(self, queryset, name, value):
        if value == 'pending':
            queryset = queryset.filter(published=False)
        elif value == 'published':
            queryset = queryset.filter(published=True)
        return queryset
