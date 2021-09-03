from .models import Account


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

def member_count(request):
    count = sum([
        Account.objects.all().count(),
        Account.objects.filter(is_spouse=True).count(),
    ])
    return count
