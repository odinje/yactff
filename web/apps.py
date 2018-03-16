from django.apps import AppConfig
from web.utils import pause_game, load_page_files


class WebConfig(AppConfig):
    name = 'web'

    def ready(self):
        import web.signals
        pause_game()  # Init game pause, first run sets to False.
        load_page_files()
