from django.contrib.auth.signals import user_logged_in
from web.utils import get_client_ip


def get_user_ip(sender, user, request, **kwargs):
    ip = get_client_ip(request)
    user.last_ip = ip
    user.save()


user_logged_in.connect(get_user_ip)
