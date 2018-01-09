from django.shortcuts import render, redirect
from django.http import Http404
from web.utils import get_or_none
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from web.models import Page, Category, Challenge, SolvedChallenge
from django.conf import settings
from django.db.models import F

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


def page(request, path=None):
    if path:
        name = path.split("/")[-1]
    else:
        name = "index"
    page = get_or_none(Page, name=name)
    if page:
        context = {"body": page.content,
                   "type": page.type}
        return render(request, "web/page.html", context)
    elif page is None and name == "index":
        context = {"body": "<h3>Index page is empty</h3>",
                   "type": "html"}
        return render(request, "web/page.html", context)
    else:
        raise Http404


@login_required
def challenges(request):
    categories = Category.objects.all()

    challenges = Challenge.objects.with_solves(team=request.user.team_id)
    return render(request, "web/challenges.html", {"challenges": challenges,
                                                   "categories": categories})


@login_required
def challenge(request, id):
    team_id = request.user.team_id
    challenge = Challenge.objects.with_solves(team=team_id, challenge=id)

    if request.method == "POST":
        if "flag" in request.POST:
            flag = request.POST["flag"]
            if challenge.is_flag(flag):
                solved = SolvedChallenge(team_id=team_id, challenge=challenge)
                solved.save()
                challenge.is_solved = True

    return render(request, "web/challenge.html", {"challenge": challenge})


@login_required
def user_profile(request):
    return render(request, "web/user_profile.html")


@login_required  # Maybe also have team requuired
def team_profile(request):
    team = request.user.team
    max_team_size = settings.MAX_TEAM_SIZE
    try:  # Move this to models.py
        challenges = SolvedChallenge.objects.annotate(title=F("challenge__title"), points=F("challenge__points")).select_related("challenge").filter(team=team)
    except:
        challenges = None
    return render(request, "web/team_profile.html", {"team": team, "team_view": True, "max_team_size": max_team_size, "challenges": challenges})


@login_required
def team_join(request):
    raise Http404
