from django.apps import AppConfig


class WebConfig(AppConfig):
    name = 'web'

    def ready(self):
        try:
            from web.models import load_page_files
            load_page_files()
        except:
            pass
