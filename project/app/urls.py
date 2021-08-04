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

    # Authentication
    path('join', views.join, name='join'),
    path('callback', views.callback, name='callback'),
    path('verify', views.verify, name='verify'),
    path('verified', views.verified, name='verified'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),

    # Account
    path('account', views.account, name='account',),
    path('student/add', views.add_student, name='add-student',),
    path('student/<str:student_id>/delete', views.delete_student, name='delete-student',),
    path('student/<str:student_id>', views.edit_student, name='edit-student',),

    # Comments
    path('comments', views.comments, name='comments',),
    path('comment/<str:comment_id>/delete', views.comment_delete, name='comment-delete',),
    path('comment/submit-written', views.submit_written_comment, name='submit-written-comment'),
    path('comment/submit-video', views.submit_video_comment, name='submit-video-comment'),
    path('comment/video-submission', views.video_submission, name='video-submission'),

    # Events
    path('event/<str:event_id>', views.event, name='event',),
    path('events', views.events, name='events',),

    # Delete
    path('delete', views.delete, name='delete',),

]
