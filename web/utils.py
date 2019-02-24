import logging
import random
import string
import os
import glob
import errno
import csv
from django.conf import settings
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from io import BytesIO
from zipfile import ZipFile
from datetime import datetime
from django.core.cache import cache

logger = logging.getLogger(__name__)


YACTFF_PAUSED_FILE = "/tmp/.yactff_paused"


def get_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except ObjectDoesNotExist:
        return None


def random_string(size=8):
    _string = "".join([random.choice(string.ascii_letters + string.digits) for n in range(size)])
    return _string


def load_page_files():
    '''
    Then read all local page file, and load it into the database.
    '''
    Page = apps.get_model("web.Page")
    for type in Page.TYPE_CHOICES:
        files = glob.glob("{0}/*{1}".format(settings.PAGE_DIR, type[0]))
        for file in files:
            name = file.split("/")[-1]
            name = name.split(".")[0]

            page, created = Page.objects.get_or_create(name=name.lower())

            if not created:
                with open(file, "r") as f:
                    page.type = type[0]
                    page.content = f.read()
                    page.save()


def _page_path(dir, name, type):
    return "{0}/{1}.{2}".format(dir, name, type)


def save_page_file(name, type, content):
    path = _page_path(settings.PAGE_DIR, name, type)
    with open(path, "w") as f:
        f.write(content)


def delete_page_file(name, type):
    path = _page_path(settings.PAGE_DIR, name, type)
    try:
        os.remove(path)
    except OSError as e:  # this would be "except OSError, e:" before Python 2.
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occurred


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def create_zip(files):
    in_memory = BytesIO()
    zip = ZipFile(in_memory, "a")

    for file in files:
        zip.writestr(file.name, file.read())

    # fix for Linux zip files read in Windows
    for file in zip.filelist:
        file.create_system = 0
    zip.close()
    return in_memory


def pause_game():
    if is_game_paused():
        cache.set("CTF_PAUSED", False)
    else:
        cache.set("CTF_PAUSED", True)


def init_pause_state():
    if not is_game_paused():
        cache.set("CTF_PAUSED", False)


def is_game_paused():
    state = cache.get("CTF_PAUSED", False)
    if state:
        return True
    else:
        return False


def _iso8601_to_datetime(time):
    return datetime.strptime(time, "%Y-%m-%d %H:%M:%S")


def is_game_started():
    if datetime.now() >= _iso8601_to_datetime(settings.CTF_START):
        return True
    return False


def is_game_ended():
    if datetime.now() >= _iso8601_to_datetime(settings.CTF_END):
        return True
    return False


def _build_game_csv_header():
    user_header = ["nickname", "email", "first_name", "last_name"]  # TODO: missing age, country, nor_cit, city
    game_header = ["placement", "team", "score"]
    for c in range(1, settings.MAX_TEAM_SIZE+1):
        _user = ["{}. {}".format(c, el) for el in user_header]
        game_header += _user
    return game_header


def write_game_csv(response, scoreboard):
    User = apps.get_model("web.User")
    writer = csv.DictWriter(response, fieldnames=_build_game_csv_header())

    writer.writeheader()
    for pos, score in enumerate(scoreboard):
        team_name = score["team_name"]
        row = {"placement": pos+1, "team": team_name, "score": score["team_score"]}
        users = User.objects.filter(team__name=team_name)
        for c, user in enumerate(users):
            row["{}. nickname".format(c+1)] = user.nickname
            row["{}. email".format(c+1)] = user.email
            row["{}. first_name".format(c+1)] = user.first_name
            row["{}. last_name".format(c+1)] = user.last_name
        writer.writerow(row)
    return response
