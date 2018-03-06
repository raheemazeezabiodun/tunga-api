from django.utils.deprecation import MiddlewareMixin

from tunga import settings


class DisableCSRFOnDebug(MiddlewareMixin):
    def process_request(self, request):
        if settings.DEBUG:
            setattr(request, '_dont_enforce_csrf_checks', True)
