from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse, JsonResponse
from web.utils import get_or_none
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required, user_passes_test
from web.models import Page, Category, Challenge, Submission, Team, get_scoreboard 
from django.conf import settings
from web.forms import TeamCreateForm, UserCreationForm, UserChangeForm
from web.decorator import team_required, not_in_team, anonymous_required



@anonymous_required
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get("email")
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=raw_password)
            login(request, user)
            return redirect("index")
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
    return render(request, "web/challenges.html", 
            {
                "challenges": challenges,
                "categories": categories
            })


@login_required
def challenge(request, id):
    user = request.user
    team_id = user.team_id
    challenge = Challenge.objects.with_solves(team=team_id, challenge=id)
    have_team = False
    
    if team_id:
        have_team = True
    if request.method == "POST" and have_team:
        if "flag" in request.POST:
            flag = request.POST["flag"]
            if challenge.is_flag(flag):
                solved = Submission(team_id=team_id, challenge=challenge, solved_by=user)
                solved.save()
                challenge.is_solved = True

    return render(request, "web/challenge.html", {"have_team": have_team, "challenge": challenge})


def scoreboard(request):
    return render(request, "web/scoreboard.html")


def api_scoreboard(request):
    scores = get_scoreboard()
    return JsonResponse(scores, safe=False)


@login_required
def user_profile(request):
    user = request.user
    team = user.team
    challenges = Submission.objects.get_solved(team=team, user=user)
    if request.method == "POST":
        pass
    else:
        userdata_form = UserChangeForm(instance=user)
        password_form =  PasswordChangeForm(user)
        return render(request, "web/user_profile.html", 
            {
                "challenges": challenges,
                "password_form": password_form,
                "userdata_form": userdata_form,
            })


@team_required
def team_profile(request):
    team = request.user.team
    challenges = Submission.objects.get_solved(team=team)
    return render(request, "web/team_profile.html", 
            {
                "team": team, 
                "team_view": True, 
                "max_team_size": settings.MAX_TEAM_SIZE, 
                "challenges": challenges
            })

@login_required
def public_team_profile(request, id):
    team = get_or_none(Team, id=id)
    if not team:
        raise Http404
    
    challenges = Submission.objects.get_solved(team=team)
    return render(request, "web/team_profile.html", 
            {
                "team": team,
                "team_view": False,
                "max_team_size": None,
                "challenges": challenges,
            })


@not_in_team
def team_create(request):
    user = request.user
    if request.method == "POST":
        form = TeamCreateForm(request.POST)
        if form.is_valid():
            team = form.save()
            user.team = team
            user.save()

            return redirect("team_profile")
    else:
        form = TeamCreateForm()
    return render(request, "web/team_create.html",
            {
                "form": form,
                "max_team_size": settings.MAX_TEAM_SIZE
            })


@not_in_team  # TODO: Rethink or redo
def team_join(request):
    user = request.user
    if request.method == "POST":
        token = request.POST["token"]
        try:
            team = Team.objects.get(token=token)
            user.team = team
            user.save()
        except:
            return HttpResponse("Team not found")
        return redirect("team_profile")
    else:
        return HttpResponse(status=405)
