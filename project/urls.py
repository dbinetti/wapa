# Third-Party
# Django
from django.conf import settings
from django.contrib import admin
from django.shortcuts import render
from django.urls import include
from django.urls import path
from django.views.defaults import bad_request
from django.views.defaults import page_not_found
from django.views.defaults import permission_denied
from django.views.defaults import server_error
from django.views.generic import TemplateView
# First-Party
from sentry_sdk import last_event_id

urlpatterns = [
    path('', include('app.urls')),
    path('admin/', admin.site.urls),
    path('django-rq/', include('django_rq.urls')),
    path('sitemap.txt', TemplateView.as_view(
        template_name='sitemap.txt',
        content_type='text/plain"',
    )),
]

if settings.DEBUG:
    import debug_toolbar

    def render_bad_request(request):
        return bad_request(request, None)


    def render_permission_denied(request):
        return permission_denied(request, None)


    def render_page_not_found(request):
        return page_not_found(request, None)


    def render_server_error(request):
        return server_error(request)

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
        path('400/', render_bad_request),
        path('403/', render_permission_denied),
        path('404/', render_page_not_found),
        path('500/', render_server_error),
    ]
else:
    def handler500(request, *args, **argv):
        return render(
            request,
            '500.html',
            {
                'sentry_dsn': settings.SENTRY_DSN,
                'sentry_event_id': last_event_id(),
            },
            status=500,
        )
