# Django
from django.urls import path
from django.views.generic import RedirectView
from django.views.generic import TemplateView

# Local
from . import views

urlpatterns = [
    # Root
    path('', views.index, name='index',),

    # Authentication
    path('callback', views.callback, name='callback'),
    path('verify', views.verify, name='verify'),
    path('verified', views.verified, name='verified'),
    path('reverify', views.reverify, name='reverify'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('join', RedirectView.as_view(url='login'), name='join'),

    # Account
    path('dashboard', views.dashboard, name='dashboard',),
    path('account', views.account, name='account',),
    path('upload-picture', views.upload_picture, name='upload-picture',),
    path('delete-picture', views.delete_picture, name='delete-picture',),
    path('delete/', views.delete, name='delete',),

    # Comments
    path('search', views.search, name='search',),
    path('confirm/<voter_pk>', views.confirm, name='confirm',),

    # Comments
    path('comments', views.comments, name='comments',),
    path('comment/<str:comment_id>/delete', views.comment_delete, name='comment-delete',),

    # Resources
    path('exemption/', RedirectView.as_view(url='exemptions'), name='exemption'),
    path('exemptions/', TemplateView.as_view(template_name='pages/exemptions.html'), name='exemptions',),
    path('resources/', TemplateView.as_view(template_name='pages/resources/index.html'), name='resources',),
    path('resources/updates/', views.updates, name='updates',),
    path('resources/meetings/', TemplateView.as_view(template_name='pages/resources/meetings/index.html'), name='meetings',),
    path('resources/plans/', TemplateView.as_view(template_name='pages/resources/plans/index.html'), name='plans',),
    path('resources/plans/quarantine/', TemplateView.as_view(template_name='pages/resources/plans/quarantine.html'), name='quarantine',),
    path('resources/plans/truenorth/', TemplateView.as_view(template_name='pages/resources/plans/truenorth.html'), name='truenorth',),
    path('resources/plans/appeal/', TemplateView.as_view(template_name='pages/resources/plans/appeal.html'), name='appeal'),
    path('resources/plans/compare/', TemplateView.as_view(template_name='pages/resources/plans/compare.html'), name='compare',),

    # Footer
    path('about/', TemplateView.as_view(template_name='footer/about.html'), name='about',),
    path('faq/', TemplateView.as_view(template_name='footer/faq.html'), name='faq',),
    path('privacy/', TemplateView.as_view(template_name='footer/privacy.html'), name='privacy',),
    path('terms/', TemplateView.as_view(template_name='footer/terms.html'), name='terms',),
    path('support/', TemplateView.as_view(template_name='footer/support.html'), name='support',),
]
