from django.apps import AppConfig

class WebConfig(AppConfig):
    name = 'web'

    def ready(self):
        try:
            from web.models import load_local_pages
            load_local_pages()
        except:
            pass
