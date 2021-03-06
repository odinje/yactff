from django.db import models
from collections import Counter
from itertools import chain
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from web.managers import UserManager, ChallengeManger, SubmissionManager
from django.db.models import F, Sum, Max
from web.utils import save_page_file, delete_page_file
from django.core.cache import cache
import uuid
import math


# remove description? Need?
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Challenge(models.Model):  # Maybe change title -> name
    title = models.CharField(max_length=200, unique=True)
    category = models.ForeignKey("Category", on_delete=models.DO_NOTHING)
    description = models.TextField(blank=True)
    points = models.IntegerField(default=0)
    key = models.CharField(max_length=200)
    active = models.BooleanField(default=False)
    author = models.ForeignKey("User", on_delete=models.DO_NOTHING)  # author
    file = models.FileField(blank=True)

    objects = ChallengeManger()

    def __str__(self):
        return self.title

    def is_flag(self, flag):
        if self.key == flag:  # Maybe update key => flag
            return True
        return False

    def solves(self):
        submission_count = Submission.objects.filter(challenge=self.id).count()
        team_count = Submission.objects.values("team").distinct().count() 
        if submission_count == 0 or team_count == 0:
            return 0
        return (submission_count / team_count)

    def calculate_dynamic_points(self):
        #https://github.com/pwn2winctf/2018/blob/master/nizkctf/scoring.py
        max_points = 500
        min_points = 50 
        K = 80.0
        V = 3.0
        solve_count = max(1, Submission.objects.filter(challenge=self.id).count())
        print(solve_count)
        value = int(max(min_points, math.floor(max_points - K*math.log((solve_count + V)/(1+V), 2))))
        self.points = value


    def save(self, *args, **kwargs):
        self.calculate_dynamic_points()
        super(Challenge, self).save(*args, **kwargs)

class Submission(models.Model):  # Include which person who solved it?
    team = models.ForeignKey("Team", on_delete=models.DO_NOTHING)
    challenge = models.ForeignKey("Challenge", on_delete=models.DO_NOTHING)
    completed = models.DateTimeField(auto_now_add=True)
    solved_by = models.ForeignKey("User", on_delete=models.DO_NOTHING)

    objects = SubmissionManager()

    class Meta:
        unique_together = ("team", "challenge")

    def save(self, *args, **kwargs):
        super(Submission, self).save(*args, **kwargs)
        c = Challenge.objects.get(pk=self.challenge_id)
        c.calculate_dynamic_points()
        c.save()
        cache.delete("scoreboard")


class Team(models.Model):
    name = models.CharField(max_length=200, unique=True)
    logo = models.ImageField(upload_to="team/logo/", max_length=255, blank=True)
    token = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.name

    def is_solved(self, challenge):
        team_solved = Submission.objects.filter(team=self.team, challenge=challenge)

        if team_solved.exists():
            return True
        else:
            return False

    def get_members(self):
        return User.objects.values("nickname").filter(team=self.id)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    nickname = models.CharField(_("nickname"), max_length=255)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    last_ip = models.TextField(_("IP address"))
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_("staff"), default=False)  # Can probably be removed since superuser is enoguh
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
        full_name = "{0} {1}".format(self.first_name, self.last_name)
        return full_name.strip()

    def get_nickname_and_team(self):
        '''
        Returns the nickname of the user, and the team name if exists.
        '''
        if self.team:
            return "{0} ({1})".format(self.nickname, self.team.name)
        else:
            return self.nickname

    def have_team(self):
        return True if self.team else False


class Page(models.Model):
    TYPE_CHOICES = (
            ("md", "markdown"),
            ("html", "html"),
    )
    name = models.CharField(max_length=20, unique=True)
    type = models.CharField(max_length=4, choices=TYPE_CHOICES, default="md")
    in_menu = models.BooleanField(default=False)
    content = models.TextField()

    def save(self, *args, **kwargs):
        save_page_file(self.name, self.type, self.content)
        super(Page, self).save(*args, **kwargs)
        cache.delete("page_{}".format(self.name))

    def delete(self):
        delete_page_file(self.name, self.type)
        cache.delete("page_{}".format(self.name))
        super(Page, self).delete()



def recalculate_score():
    challenges = Challenge.objects.all()
    for c in challenges:
        c.calculate_dynamic_points()
        c.save()

def get_scoreboard():
    #recalculate_score() # Takes time, but ensure correct score
    scores = Submission.objects.values(team_id=F("team__id"), team_name=F("team__name"))
    scores = scores.annotate(last_submission=Max("completed"), team_score=Sum("challenge__points"))
    scores = scores.order_by("-team_score", "last_submission")

    return list(scores)


def email_user(user_id, subject, message, from_email=None, **kwargs):
    '''
    Sends an email to this User.
    '''
    try:
        user = User.objects.get(id=user_id)
        send_mail(subject, message, from_email, [user.email], **kwargs)
    except:
        pass
