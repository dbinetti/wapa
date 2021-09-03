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
    path('robots.txt', TemplateView.as_view(
        template_name='root/robots.txt',
        content_type='text/plain"',
    )),
    path('sitemap.txt', TemplateView.as_view(
        template_name='root/sitemap.txt',
        content_type='text/plain"',
    )),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

def handler400(request, *args, **argv):
    return render(
        request,
        'root/400.html',
        context={},
        status=400,
    )

def handler403(request, *args, **argv):
    return render(
        request,
        'root/403.html',
        context={},
        status=403,
    )

def handler404(request, *args, **argv):
    return render(
        request,
        'root/404.html',
        context={},
        status=404,
    )

def handler500(request, *args, **argv):
    return render(
        request,
        'root/500.html',
        {
            'sentry_dsn': settings.SENTRY_DSN,
            'sentry_event_id': last_event_id(),
        },
        status=500,
    )
