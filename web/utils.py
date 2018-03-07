import logging
import random
import string
import os
import glob
import errno
from django.conf import settings
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from io import BytesIO
from zipfile import ZipFile
from datetime import datetime

logger = logging.getLogger(__name__)


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

            with open(file, "r") as f:
                try:
                    Page.objects.get_or_create(name=name.lower(), type=type[0], content=f.read())
                except:
                    print("Database problem")


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


# TODO: Apply for caching and syncing
def pause_game():
    state = os.environ.pop("YACTFF_PAUSED", None)
    if state is None or state == "true":
        os.environ["YACTFF_PAUSED"] = "false"
    else:
        os.environ["YACTFF_PAUSED"] = "true"


def is_game_paused():
    state = os.environ["YACTFF_PAUSED"]
    if state == "true":
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
