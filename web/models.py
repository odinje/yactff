from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver



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

def _dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)


class ChallengeManger(models.Manager):
    def with_solves(self, team, challenge=None):
        if challenge:
            challenges = Challenge.objects.get(id=challenge)
            try:
                SolvedChallenge.objects.get(challenge=challenge, team=team)
                challenges.is_solved = True
            except:
                challenges.is_solved = False
        else:
            challenges = Challenge.objects.all()
            solves = SolvedChallenge.objects.filter(team=team)

            for challenge in challenges:
                for solve in solves:
                    if solve.challenge_id == challenge.id:
                        challenge.is_solved = True
                        break
                    else:
                        challenge.is_solved = False
        
        return challenges

        #from django.db import connection
        #with connection.cursor() as cursor:
        #    if challenge:
        #        challenge_sql_statement = "AND c.id = {0}".format(challenge)
        #    else:
        #        challenge_sql_statement = ""
        #   
        #    cursor.execute("""
        #        SELECT c.id, c.title, c.category_id, c.description, 
        #            c.points, c.active, c.author_id, (CASE WHEN sg.challenge_id = c.id
        #                                                THEN 1
        #                                                ELSE 0 END) as is_solved
        #        FROM web_challenge c, web_solvedchallenge sg
        #        WHERE sg.team_id = {0} {1}""".format(team, challenge_sql_statement))
            
            #self.result_list = []
            #for row in cursor.fetchall():
            #    p = self.model(id=row[0], title=row[1], category_id=row[2], description=row[3], points=row[4], active=row[5], author_id=row[6])
            #    p.is_solved = row[7]
            #    result_list.append(p)
            #return self.result_list
        #    return _dictfetchall(cursor)

class Challenge(models.Model): # Maybe change title -> name
    #contest = models.ForeignKey("Competition", on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=200, unique=True)
    category = models.ForeignKey("Category", on_delete=models.DO_NOTHING)
    description = models.TextField()
    points = models.IntegerField()
    key = models.CharField(max_length=200)
    active = models.BooleanField(default=False)
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True)  # author
   
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



class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    team = models.ForeignKey("Team", on_delete=models.DO_NOTHING)



class Page(models.Model):
    page_dir = FileSystemStorage(location=settings.PAGE_DIR)
    name = models.CharField(max_length=20, unique=True)
    path = models.CharField(max_length=20, unique=True)
    type = models.CharField(max_length=4, default="html")
    in_menu = models.BooleanField()
    file = models.FileField(storage=page_dir, null=True)
    #content = models.TextField(default="Index\n#####")
