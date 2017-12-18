from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.conf import settings



# This class can be removed, and all options places within settings. No need to
# define this in a database.
#class Competition(models.Model):
#    title = models.CharField(max_length=200, unique=True)
#    description = models.TextField()
#    slug = models.SlugField(max_length=200, unique=True)
#    active = models.BooleanField(default=False)
#    start = models.DateTimeField()
#    stop = models.DateTimeField()
#
#    def _str_(self):
#        return self.title


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)


class Challenge(models.Model): # Maybe change title -> name
    #contest = models.ForeignKey("Competition", on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=200, unique=True)
    category = models.ForeignKey("Category", on_delete=models.DO_NOTHING)
    description = models.TextField()
    points = models.IntegerField()
    key = models.CharField(max_length=200)
    active = models.BooleanField(default=False)
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True)  # author
    
    def _str_(self):
        return self.title

    def is_flag(self, flag):
        if self.key == flag: # Maybe update key => flag
            return True
        return False



class SolvedChallenge(models.Model): #Include which person who solved it?
    team = models.ForeignKey("Team", on_delete=models.DO_NOTHING) 
    challenge = models.ForeignKey("Challenge", on_delete=models.DO_NOTHING)
    completed = models.DateTimeField(auto_now_add=True)



class Team(models.Model):
    name = models.CharField(max_length=200, unique=True)
    logo = models.ImageField(upload_to="team/logo/", max_length=255, blank=True) 



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
