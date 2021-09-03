from django.core.cache import cache


def avatar(request):
    return {
        'AVATAR': {
            'format': 'png',
            'default_image': "wapa:avatar.png",
            'transformation': [
                {'height': 80, 'width': 80},
            ],
        }
    }

def metrics(request):
    member_count = cache.get('member_count')
    comment_count = cache.get('comment_count')
    student_count = cache.get('student_count')
    metrics = {
        'METRICS' : {
            'members': member_count,
            'comments': comment_count,
            'students': student_count,
        }
    }
    return metrics
