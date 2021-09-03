# Django
from django.urls import path
from django.views.generic import TemplateView

# Local
from . import views

urlpatterns = [
    # Root
    path('', views.index, name='index',),

    # Footer
    path('about/', TemplateView.as_view(template_name='app/pages/about.html'), name='about',),
    path('faq/', TemplateView.as_view(template_name='app/pages/faq.html'), name='faq',),
    path('privacy/', TemplateView.as_view(template_name='app/pages/privacy.html'), name='privacy',),
    path('terms/', TemplateView.as_view(template_name='app/pages/terms.html'), name='terms',),
    path('support/', TemplateView.as_view(template_name='app/pages/support.html'), name='support',),
    path('transcript/', TemplateView.as_view(template_name='app/pages/transcript.html'), name='transcript',),
    path('truenorth/', TemplateView.as_view(template_name='app/pages/north.html'), name='truenorth',),

    # Plan
    # path('compare/', TemplateView.as_view(template_name='app/pages/compare.html'), name='compare',),
    path('metrics/', TemplateView.as_view(template_name='app/pages/metrics.html'), name='metrics',),
    # path('plan/', TemplateView.as_view(template_name='app/pages/plan.html'), name='plan',),
    path('revisions/', TemplateView.as_view(template_name='app/pages/revisions.html'), name='revisions',),

    # Authentication
    path('join', views.join, name='join'),
    path('callback', views.callback, name='callback'),
    path('verify', views.verify, name='verify'),
    path('verified', views.verified, name='verified'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),

    # Dashboard
    path('dashboard', views.dashboard, name='dashboard',),


    path('appeal', views.appeal, name='appeal'),

    # Account
    path('account', views.account, name='account',),
    path('upload-picture', views.upload_picture, name='upload-picture',),
    path('delete-picture', views.delete_picture, name='delete-picture',),

    # Comments
    path('comments', views.comments, name='comments',),
    path('comment/<str:comment_id>', views.comment, name='comment',),
    path('comment/<str:comment_id>/delete', views.comment_delete, name='comment-delete',),

    path('story/delete/', views.story_delete, name='story-delete',),
    path('story/', views.story, name='story',),

    # Events
    path('event/<str:event_id>', views.event, name='event',),
    path('events', views.events, name='events',),
    path('plan/', views.plan, name='plan',),
    path('compare/', views.compare, name='compare',),

    # Share
    path('share/', views.share, name='share'),

    # Delete
    path('delete/', views.delete, name='delete',),

]
