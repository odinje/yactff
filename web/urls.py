from django.conf.urls import url
from django.urls import re_path, path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    url("^$", views.index, name="index"),
    re_path(r"^page/(?P<path>\w+)/$", views.pages, name="pages"),
    url(r'^login/$', auth_views.login, {"template_name": "web/login.html"}, name='login'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    re_path(r"^admin/web/page/(?P<id>\d+)/change/(?P<filename>.*)/$", views.download_page_file, name="download_page_file")
]

