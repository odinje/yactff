from django.apps import AppConfig
from web.utils import pause_game

class WebConfig(AppConfig):
    name = 'web'

    def ready(self):
        import web.signals
        pause_game()  # Init game pause, first run sets to False.
        try:
            from web.utils import load_page_files
            load_page_files()
        except:
            pass
