from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.conf import settings


class Competition(models.Model):
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    slug = models.SlugField(max_length=200, unique=True)
    active = models.BooleanField(default=False)
    start = models.DateTimeField()
    stop = models.DateTimeField()

    def _str_(self):
        return self.title


class Category(models.Model):
    title = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField()


class Challenge(models.Model):
    contest = models.ForeignKey("Competition", on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    category = models.ForeignKey("Category", on_delete=models.DO_NOTHING)
    description = models.TextField()
    points = models.IntegerField()
    key = models.CharField(max_length=200)
    active = models.BooleanField(default=False)
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING)  # author

    def _str_(self):
        return self.title


class SolvedChallenge(models.Model):
    team = models.ForeignKey("Team", on_delete=models.DO_NOTHING)
    challenge = models.ForeignKey("Challenge", on_delete=models.DO_NOTHING)
    completed = models.DateTimeField(auto_now_add=True)


class Team(models.Model):
    name = models.CharField(max_length=200, unique=True)
    logo = models.ImageField(upload_to="team/logo/", max_length=255) 
    solved_challenges = models.ManyToManyField("Challenge", through="SolvedChallenge")


class Player(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    team = models.ForeignKey("Team", on_delete=models.DO_NOTHING)


class Page(models.Model):
    page_dir = FileSystemStorage(location=settings.PAGE_DIR)
    name = models.CharField(max_length=20, unique=True)
    path = models.CharField(max_length=20, unique=True)
    type = models.CharField(max_length=4, default="html")
    in_menu = models.BooleanField()
    file = models.FileField(storage=page_dir, null=True)
    #content = models.TextField(default="Index\n#####")
