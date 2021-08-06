def avatar(request):
    return {
        'AVATAR': {
            'format': 'png',
            'transformation': [
                {'height': 100, 'width': 100},
            ],
        }
    }
