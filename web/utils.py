import logging
import random
import string
import os
import glob
import errno
from django.conf import settings
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist

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
    except OSError as e: # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occurred


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
