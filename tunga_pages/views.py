import re

from django.contrib.sitemaps import Sitemap
from dry_rest_permissions.generics import DRYPermissions, DRYObjectPermissions
from rest_framework import viewsets

from tunga_pages.models import SkillPage, BlogPost
from tunga_pages.serializers import SkillPageSerializer, BlogPostSerializer


class SkillPageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Skill Page Resource
    """
    queryset = SkillPage.objects.all()
    serializer_class = SkillPageSerializer
    permission_classes = [DRYObjectPermissions]
    lookup_url_kwarg = 'keyword'
    lookup_field = 'keyword'
    lookup_value_regex = '[^/]+'
    search_fields = ('keyword', 'skill__name')


class SkillPagesSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return SkillPage.objects.filter()

    def lastmod(self, obj):
        return obj.created_at


class BlogPostViewSet(viewsets.ModelViewSet):
    """
    Blog Post Resource
    """
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [DRYObjectPermissions]
    lookup_url_kwarg = 'post_id'
    lookup_field = 'id'
    lookup_value_regex = '[^/]+'
    search_fields = ('^slug', '^title')

    def get_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        user_id = self.kwargs[lookup_url_kwarg]
        if re.match(r'[^\d]', user_id):
            self.lookup_field = 'slug'
        return super(BlogPostViewSet, self).get_object()
