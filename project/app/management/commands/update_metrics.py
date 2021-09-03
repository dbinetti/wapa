from django.apps import apps
from django.core.cache import cache
from django.core.management.base import BaseCommand

Account = apps.get_model("app", "Account")
Comment = apps.get_model("app", "Comment")
Student = apps.get_model("app", "Student")


class Command(BaseCommand):
    def handle(self, *args, **options):
        member_count = sum([
            Account.objects.all().count(),
            Account.objects.filter(is_spouse=True).count(),
        ])
        cache.set('member_count', member_count, timeout=None)
        comment_count = Comment.objects.all().count()
        cache.set('comment_count', comment_count, timeout=None)

        student_count = Student.objects.all().count()
        cache.set('student_count', student_count, timeout=None)
        return
