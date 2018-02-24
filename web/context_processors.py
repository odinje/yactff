from django.conf import settings
from web.models import Page
from web.utils import (
        is_game_paused,
        is_game_started,
        is_game_ended,
        )


def header(request):
    pages = {"Scoreboard": "/scoreboard",
             "Challenges": "/challenges"}

    obj = Page.objects.all()
    for page in obj:
        if page.in_menu:
            pages[page.name.title()] = "/page/" + page.name
    return {
            "ctf_name": settings.CTF_NAME,
            "pages_navbar": sorted(pages.items()),
            "paused": is_game_paused(),
            "game_started": is_game_started(),
            "game_ended": is_game_ended(),
            }
