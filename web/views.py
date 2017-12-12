from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import user_passes_test
from web.utils import load_page, get_or_none
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from web.models import Page, Category, Challenge, Team, SolvedChallenges
from django.conf import settings
import os

def index(request):
    context = {'body': load_page(settings.PAGE_DIR + "index.md"), "type": "md"}
    return render(request, "web/index.html", context)

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'web/signup.html', {'form': form})


def pages(request, path):
    page = get_or_none(Page, path=path)
    
    if page:
        context = {"body": load_page(page.file.path),
            "type": page.type}
        return render(request, "web/page.html", context)
    else:
        raise Http404


def challenges(request):
    user = request.user
    if user.is_authenticated or settings.ALLOW_ANONYMOUS_CHALLANGE_VIEW:
        team_solved = None
        categories = Category.objects.all()
        challenges = Challenge.objects.values("title", "category", "points",
                                                                     "active")
        if user.is_authenticated:
            team = get_or_none(Team, user=user)
            team_solved = SolvedChallenges.objects.values("challenge")
        

        return render(request, "web/challenges.html", {"challenges": challenges,
                                                    "categories": categories,
                                                    "solved": team_solved})
    else:
        raise Http404 #TODO!
            
    

@user_passes_test(lambda u: u.is_superuser) #TODO: Maybe change to is_staff?
def download_page_file(request, id, filename):
    filepath = settings.PAGE_DIR + filename 
    response = HttpResponse(load_page(filepath), "applicaion/text")
    response['Content-Disposition'] = "attachment; filename={0}".format(filename)
    response['Content-Length'] = os.path.getsize(filepath)
    return response
