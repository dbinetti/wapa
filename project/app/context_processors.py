def avatar(request):
    return {
        'AVATAR': {
            'format': 'png',
            'transformation': [
                {'height': 80, 'width': 80},
            ],
        }
    }
