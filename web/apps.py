from django.apps import AppConfig


class WebConfig(AppConfig):
    name = 'web'

    def ready(self):
        import web.signals
        try:
            from web.utils import load_page_files
            load_page_files()
        except:
            pass
