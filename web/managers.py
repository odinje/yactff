from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.apps import apps
from django.db.models import F, Sum

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class ChallengeManger(models.Manager):
    def with_solves(self, team, challenge=None):
        challenges = apps.get_model("web.Challenge")
        solves = apps.get_model("web.Submission")
        
        if challenge:
            challenges = challenges.objects.get(id=challenge)
            try:
                solves.objects.get(challenge=challenge, team=team)
                challenges.is_solved = True
            except:
                challenges.is_solved = False
        else:
            challenges = challenges.objects.all()
            solves = solves.objects.filter(team=team)

            for challenge in challenges:
                for solve in solves:
                    if solve.challenge_id == challenge.id:
                        challenge.is_solved = True
                        break
                    else:
                        challenge.is_solved = False

        return challenges


class SubmissionManager(models.Manager):
    def get_solved(self, team=None, user=None):
        if team is None and user is None:
            print("Both canot be none")
            return None
        elif user is not None:
            filter = { "team": team, "solved_by": user } 
        elif team is not None:
            filter = { "team": team }
        try:
            submission = apps.get_model("web.Submission")
            return submission.objects.annotate(title=F("challenge__title"), points=F("challenge__points")).select_related("challenge", "solved_by").filter(**filter)
        except:
            return None

    def scoreboard(self):
        return self.select_related("team").annotate(score=Sum("challenge__points"))
        #return submission.objects.values("team").aggregate(score=Sum("challenge__points"))


class TeamManager(models.Manager):
    def scoreboard(self):
        submission = apps.get_model("web.Submission")
        scores = submission.objects.values(team_id=F("team__id"), team_name=F("team__name")).annotate(team_score=Sum("challenge__points"))
        return list(scores)
