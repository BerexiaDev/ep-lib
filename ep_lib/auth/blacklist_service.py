from .models.black_list_token import BlacklistToken


def save_token(token):
    blacklist_token = BlacklistToken(token=token)
    try:
        blacklist_token.save()
        response_object = {
            'status': 'success',
            'message': 'Successfully logged out.'
        }
        return response_object, 200
    except Exception as e:
        response_object = {
            'status': 'fail',
            'message': e
        }
        return response_object, 200
