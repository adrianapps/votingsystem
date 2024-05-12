import urllib
import json

from votingsystem import settings


def verify_recaptcha(recaptcha_response):
    data = urllib.parse.urlencode({
        'secret': settings.CAPTCHA_PRIVATE_KEY,
        'response': recaptcha_response
    }).encode('utf-8')
    req = urllib.request.Request('https://www.google.com/recaptcha/api/siteverify', data=data)
    response = urllib.request.urlopen(req)
    result = json.loads(response.read())
    return result.get('success', False)
