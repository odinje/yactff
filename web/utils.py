import logging

logger = logging.getLogger(__name__)


def load_page(filepath):
    try:
        with open(filepath, "r") as file:
            return file.read()
    except IOError:
        logger.error("There was an error opening {}!".format(filepath))
        return


