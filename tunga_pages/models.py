from __future__ import unicode_literals

import datetime

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.text import slugify
from dry_rest_permissions.generics import allow_staff_or_superuser

from tunga import settings
from tunga_profiles.models import Skill


@python_2_unicode_compatible
class SkillPage(models.Model):
    keyword = models.CharField(max_length=100, primary_key=True)
    skill = models.ForeignKey(Skill, on_delete=models.DO_NOTHING)
    welcome_header = models.CharField(max_length=70)
    welcome_sub_header = models.CharField(max_length=150)
    welcome_cta = models.CharField(max_length=50)
    pitch_header = models.CharField(max_length=100)
    pitch_body = models.CharField(max_length=450)
    pitch_image = models.ImageField(upload_to='pages/uploads/%Y/%m/%d', blank=True, null=True)
    content_header = models.CharField(max_length=100)
    content_sub_header = models.CharField(max_length=100, blank=True, null=True)
    content = models.TextField()
    content_image = models.ImageField(upload_to='pages/uploads/%Y/%m/%d', blank=True, null=True)
    story_interlude_one_image = models.ImageField(upload_to='pages/uploads/%Y/%m/%d', blank=True, null=True)
    story_interlude_one_text = models.CharField(max_length=200)
    story_interlude_one_cta = models.CharField(max_length=30)
    story_body_two = models.TextField()
    story_interlude_two_image = models.ImageField(upload_to='pages/uploads/%Y/%m/%d', blank=True, null=True)
    story_interlude_two_text = models.CharField(max_length=200)
    story_body_three = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} Page'.format(self.keyword)

    class Meta:
        ordering = ['-created_at']

    def get_absolute_url(self):
        return '/{}/'.format(self.keyword)

    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        return True

    @allow_staff_or_superuser
    def has_object_write_permission(self, request):
        return request.user == self.user


@python_2_unicode_compatible
class SkillPageProfile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    page = models.ForeignKey(SkillPage, on_delete=models.CASCADE)
    intro = models.CharField(max_length=100)
    priority = models.IntegerField(default=100)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='skill_profiles_created',
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} - {}'.format(self.user.get_short_name() or self.user.username, self.page)

    class Meta:
        unique_together = ('user', 'page')
        ordering = ['-priority', '-created_at']
        verbose_name = 'skill page profile'

    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        return True

    @allow_staff_or_superuser
    def has_object_write_permission(self, request):
        return self.has_object_write_permission(request)


@python_2_unicode_compatible
class BlogPost(models.Model):
    slug = models.SlugField(max_length=50, unique=True)
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='blog/%Y/%m/%d', blank=True, null=True)
    body = models.TextField()
    published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Blog Post | {}'.format(self.title)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.slug = slugify(self.title)
        if self.published and not self.published_at:
            self.published_at = datetime.datetime.utcnow()
        super(BlogPost, self).save(
            force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields
        )

    class Meta:
        ordering = ['-created_at']

    def get_absolute_url(self):
        return '/blog/{}/'.format(self.slug)

    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        return True

    @allow_staff_or_superuser
    def has_object_write_permission(self, request):
        return request.user == self.created_by
