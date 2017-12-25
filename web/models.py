from django.db import models
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _

from web.managers import UserManager, ChallengeManger
#from web.managers import ChallengeManger


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
    author = models.ForeignKey("User", on_delete=models.DO_NOTHING, blank=True)  # author
   
    objects = ChallengeManger()
   
    def _str_(self):
        return self.title

    def is_flag(self, flag):
        if self.key == flag: # Maybe update key => flag
            return True
        return False


# Rename to submissions
class SolvedChallenge(models.Model): #Include which person who solved it?
    team = models.ForeignKey("Team", on_delete=models.DO_NOTHING) 
    challenge = models.ForeignKey("Challenge", on_delete=models.DO_NOTHING)
    completed = models.DateTimeField(auto_now_add=True)


class Team(models.Model):
    name = models.CharField(max_length=200, unique=True)
    logo = models.ImageField(upload_to="team/logo/", max_length=255, blank=True) 

    def is_solved(self, challenge):
        team_solved = SolvedChallenge.objects.filter(team=self.team, challenge=challenge)

        if team_solved.exists():
            return True
        else:
            return False

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    nickname = models.CharField(_("nickname"), max_length=255)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_("staff"), default=True)
    team = models.ForeignKey("Team", on_delete=models.DO_NOTHING, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["nickname"]

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_nickname_and_team(self):
        '''
        Returns the nickname of the user, and the team name if exists.
        '''
        if self.team:
            return  "{0} ({1})".format(self.nickname, self.team.name)
        else:
            return self.nickname

    def email_user(self, subject, message, from_email=None, **kwargs):
        '''
        Sends an email to this User.
        '''
        send_mail(subject, message, from_email, [self.email], **kwargs)


class Page(models.Model):
    page_dir = FileSystemStorage(location=settings.PAGE_DIR)
    name = models.CharField(max_length=20, unique=True)
    path = models.CharField(max_length=20, unique=True)
    type = models.CharField(max_length=4, default="html")
    in_menu = models.BooleanField()
    file = models.FileField(storage=page_dir, null=True)
    #content = models.TextField(default="Index\n#####")
