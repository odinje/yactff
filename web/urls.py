from django.urls import re_path, path
from django.contrib.auth import views as auth_views
from web import views

urlpatterns = [
    path("", views.page, name="index"),
    path("challenges/", views.challenges, name="challenges"),
    path("challenge/<int:id>", views.challenge, name="challenge"),
    re_path(r"^page/(?P<path>\w+)/$", views.page, name="page"),
    path("login/", auth_views.login, {"template_name": "web/login.html"}, name='login'),
    path("signup/", views.signup, name='signup'),
    path("user/logout", auth_views.logout, {'next_page': '/'}, name='logout'),
    path("user/profile", views.user_profile, name="user_profile"),
    path("team/profile", views.team_profile, name="team_profile"),
    path("team/join", views.team_join, name="team_join")
]
