from django.conf import settings
from .models import Page


def header(request):
    pages = {"Scoreboard": "/scoreboard",
             "Challenges": "/challenges"}

    obj = Page.objects.all()
    for page in obj:
        if page.in_menu:
            pages[page.name.title()] = "/page/" + page.name
    return {"ctf_name": settings.CTF_NAME, "pages_navbar": sorted(pages.items())}
