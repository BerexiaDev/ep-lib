from flask import current_app
import requests

def verify_captcha(token):
    url = 'https://www.google.com/recaptcha/api/siteverify'
    data = {
        'secret': current_app.config['RECAPTCHA_SECRET_KEY'],
        'response': token
    }
    response = requests.post(url, data=data)
    result = response.json()
    return result.get('success', False)