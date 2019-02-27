from django.urls import re_path, path
from django.contrib.auth import views as auth_views
from web import views
from django.conf import settings
from web.forms import LoginForm

LoginForm.signup_open = settings.SIGNUP_OPEN

urlpatterns = [
    path("", views.PageView.as_view(), name="index"),
    path("challenges/", views.ChallengesView.as_view(), name="challenges"),
    path("challenge/<int:id>", views.ChallengeView.as_view(), name="challenge"),
    path("admin/challenges/", views.AdminCompetitionView.as_view(), name="admin-competition"),
    path("admin/challenge/add", views.AdminChallengeCreate.as_view(), name="admin-challenge-add"),
    path("admin/challenge/<int:pk>", views.AdminChallengeUpdate.as_view(), name="admin-challenge-edit"),
    path("admin/category/add", views.AdminCategoryCreate.as_view(), name="admin-category-add"),
    path("admin/submission/action/remove/<int:id>", views.submission_remove, name="submission_remove"),
    path("scoreboard/", views.scoreboard, name="scoreboard"),
    path("scoreboard.json/", views.scoreboard_json, name="scoreboard_json"),
    re_path(r"^page/(?P<path>\w+)/$", views.PageView.as_view(), name="page"),
    path("admin/page/action/add/", views.page_add, name="page_add"),
    path("admin/page/action/remove/<int:id>", views.page_remove, name="page_remove"),
    path("admin/game/pause", views.pause_game, name="pause_game"),
    path("admin/game/export", views.export_game_csv, name="export_game_csv"),
    path("login/", auth_views.LoginView.as_view(template_name="web/login.html", authentication_form=LoginForm), name='login'),
    path("signup/", views.signup, name='signup'),
    re_path(r"^user/activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$", views.user_activate, name="user_activate"),
    path("user/logout", auth_views.LogoutView.as_view(next_page='/'), name='logout'),
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
