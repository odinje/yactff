from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from web.utils import (
        is_game_paused,
        is_game_started,
        is_game_ended,
        )

def _in_team(user):
    if user.is_authenticated:
        if user.have_team():
                return True
    return False


def _not_in_team(user):
    if user.is_authenticated:
        if not user.have_team():
                return True
    return False


def team_required(user=None):
    decorator = user_passes_test(_in_team, login_url="user_profile",
                                 redirect_field_name=None)
    if user:
        return decorator(user)
    return decorator


def not_in_team(user=None):
    decorator = user_passes_test(_not_in_team, login_url="team_profile",
                                 redirect_field_name=None)
    if user:
        return decorator(user)
    return decorator


def anonymous_required(user):
    decorator = user_passes_test(lambda u: not u.is_authenticated,
                                 login_url="index", redirect_field_name=None)
    if user:
        return decorator(user)
    return decorator


def admin_required(user):
    decorator = user_passes_test(lambda u: u.is_superuser,
                                 login_url="index", redirect_field_name=None)
    if user:
        return decorator(user)
    return decorator


def game_active(user):
    def check_game_active(user):
        if (user.is_superuser or (not is_game_paused() and
                is_game_started() and not is_game_ended())):
            return True
        return False
    decorator = user_passes_test(check_game_active, login_url="index", redirect_field_name=None)
    if user:
        return decorator(user)
    return decorator

