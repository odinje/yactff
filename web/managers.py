from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.apps import apps

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
        solves = apps.get_model("web.SolvedChallenge")
        
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
