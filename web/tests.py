from django.test import TestCase
from web.models import Player, Team, SolvedChallenge, Challenge, Category
from django.contrib.auth.models import User
from django.db import connection
from django.test.utils import override_settings
from django.conf import settings

class SolvedChallangeTestCase(TestCase):
#    @override_settings(DEBUG=True)
    def setUp(self):
        user = User.objects.create_user("Bob", "bob@eve.com", "secret123")
        author = User.objects.create_user("Author", "author@eve.com", "secret123")
        user.save()
        team = Team.objects.create(name="Alice")
        team.save()
        misc = Category.objects.create(name="Misc")
        misc.save()
        challenge = Challenge.objects.create(title="Misc100", category=misc,
                description="Test misc 100", points=100, key="flag{misc}",
                active=True, author=author)
        challenge.save()
        Player.objects.create(user=user,team=team)

        solved = SolvedChallenge.objects.create(team=team,
                challenge=challenge) 
 #       print(connection.queries)
        solved.save()

    @override_settings(DEBUG=True)
    def test_solved_Challanges(self):
        team = Team.objects.get(name="Alice")
        solved = SolvedChallenge.objects.get(team=team)
        print(connection.queries)
        self.assertEqual(solved.challenge.title, "Misc100")
