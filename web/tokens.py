from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from web.models import User

def generate_user_token_message(user, domain, https, template):
    print(https)
    message = render_to_string(template,
        {
            "user": user,
            "domain": domain,
            "protocol": "https" if https else "http",
            "uid": urlsafe_base64_encode(force_bytes(user.pk)).decode("utf-8"),
            "token": account_token.make_token(user),
        })
    return message


def verify_user_token(uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_token.check_token(user, token):
        return user
    return None

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )


account_token = TokenGenerator()
