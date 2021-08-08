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
