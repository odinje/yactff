from django.urls import re_path, path
from django.contrib.auth import views as auth_views
from web import views

urlpatterns = [
    path("", views.page, name="index"),
    path("challenges/", views.challenges, name="challenges"),
    path("challenge/<int:id>", views.challenge, name="challenge"),
    path("admin/challenge/action/add", views.challenge_add, name="challenge_add"),
    path("admin/submission/action/remove/<int:id>", views.submission_remove, name="submission_remove"),
    path("scoreboard/", views.scoreboard, name="scoreboard"),
    path("scoreboard.json/", views.scoreboard_json, name="scoreboard_json"),
    re_path(r"^page/(?P<path>\w+)/$", views.page, name="page"),
    path("admin/page/action/add/", views.page_add, name="page_add"),
    path("admin/page/action/remove/<int:id>", views.page_remove, name="page_remove"),
    path("admin/game/pause", views.pause_game, name="pause_game"),
    path("login/", auth_views.login, {"template_name": "web/login.html"}, name='login'),
    path("signup/", views.signup, name='signup'),
    re_path(r"^user/activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$", views.user_activate, name="user_activate"),
    path("user/logout", auth_views.logout, {'next_page': '/'}, name='logout'),
    path("user/profile", views.user_profile, name="user_profile"),
    path("user/password/reset", views.user_password_reset, name="user_password_reset"),
    re_path(r"^user/password/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$", views.user_password_reset_confirm, name="user_password_reset_confirm"),
    path("admin/user/all", views.user_all, name="user_all"),
    path("admin/user/<int:id>", views.user_show, name="user_show"),
    path("team/profile", views.team_profile, name="team_profile"),
    path("team/<int:id>", views.public_team_profile, name="public_team_profile"),
    path("team/join", views.team_join, name="team_join"),
    path("team/create", views.team_create, name="team_create")
]


#http://garmoncheg.blogspot.no/2012/07/django-resetting-passwords-with.html
