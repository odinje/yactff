from django.contrib.auth.decorators import user_passes_test

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



def anonymous_required(u):
    return user_passes_test(lambda u: not u.is_authenticated,
            login_url="index", redirect_field_name=None)
