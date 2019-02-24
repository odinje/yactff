from django.apps import AppConfig
from web.utils import init_pause_state, load_page_files


class WebConfig(AppConfig):
    name = 'web'

    def ready(self):
        import web.signals
        try:
            init_pause_state()
            load_page_files()
        except:
            pass
