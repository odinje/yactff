import logging
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger(__name__)


def get_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except ObjectDoesNotExist:
        return None
