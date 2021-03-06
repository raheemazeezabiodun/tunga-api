from django.contrib import admin

from tunga_utils.models import ContactRequest, SiteMeta, InviteRequest, ExternalEvent, SearchEvent


class AdminAutoCreatedBy(admin.ModelAdmin):
    exclude = ('created_by',)

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        obj.save()


class ReadOnlyModelAdmin(admin.ModelAdmin):
    actions = None

    def get_readonly_fields(self, request, obj=None):
        if not self.fields:
            return [
                field.name
                for field in self.model._meta.fields
                if field != self.model._meta.pk
            ]
        else:
            return self.fields

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        if request.method not in ('GET', 'HEAD'):
            return False
        else:
            return super(ReadOnlyModelAdmin, self).has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        pass


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'email', 'item', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('email', 'fullname')


@admin.register(SiteMeta)
class SiteMetaAdmin(AdminAutoCreatedBy):
    list_display = ('meta_key', 'meta_value', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('meta_key',)


@admin.register(InviteRequest)
class InviteRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'country')
    list_filter = ('country',)
    search_fields = ('name', 'email')


@admin.register(ExternalEvent)
class ExternalEventAdmin(ReadOnlyModelAdmin):
    list_display = ('source', 'payload', 'created_at', 'notification_sent_at')
    list_filter = ('source',)
    search_fields = ('payload',)


@admin.register(SearchEvent)
class SearchEventAdmin(ReadOnlyModelAdmin):
    list_display = ('user', 'email', 'query', 'page', 'created_at', 'updated_at')
    search_fields = ('query', 'email', 'user__email')
