# Django
from django.urls import path
from django.views.generic import TemplateView

# Local
from . import views

urlpatterns = [
    # Root
    path('', views.index, name='index',),

    # Authentication
    path('join', views.join, name='join'),
    path('callback', views.callback, name='callback'),
    path('verify', views.verify, name='verify'),
    path('verified', views.verified, name='verified'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),

    # Pages
    path('truenorth/', TemplateView.as_view(template_name='pages/truenorth.html'), name='truenorth',),
    path('resources/', TemplateView.as_view(template_name='pages/resources.html'), name='resources',),
    path('quarantine/', TemplateView.as_view(template_name='pages/quarantine.html'), name='quarantine',),
    path('appeal', TemplateView.as_view(template_name='pages/appeal.html'), name='appeal'),
    path('plan/', TemplateView.as_view(template_name='pages/plan.html'), name='plan',),
    path('compare/', TemplateView.as_view(template_name='pages/compare.html'), name='compare',),


    # Account
    path('dashboard', views.dashboard, name='dashboard',),
    path('account', views.account, name='account',),
    path('upload-picture', views.upload_picture, name='upload-picture',),
    path('delete-picture', views.delete_picture, name='delete-picture',),

    # Comments
    path('comments', views.comments, name='comments',),
    path('comment/<str:comment_id>/delete', views.comment_delete, name='comment-delete',),

    # Story
    path('story/', views.story, name='story',),
    path('story/delete/', views.story_delete, name='story-delete',),

    # Events
    path('event/<str:event_id>', views.event, name='event',),
    path('events', views.events, name='events',),

    # Share
    path('share/', TemplateView.as_view(template_name='pages/share.html'), name='share'),

    # Delete
    path('delete/', views.delete, name='delete',),

    # Footer
    path('about/', TemplateView.as_view(template_name='footer/about.html'), name='about',),
    path('faq/', TemplateView.as_view(template_name='footer/faq.html'), name='faq',),
    path('privacy/', TemplateView.as_view(template_name='footer/privacy.html'), name='privacy',),
    path('terms/', TemplateView.as_view(template_name='footer/terms.html'), name='terms',),
    path('support/', TemplateView.as_view(template_name='footer/support.html'), name='support',),
]
