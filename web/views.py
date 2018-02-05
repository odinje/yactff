from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, JsonResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required, user_passes_test
from web.models import Page, Category, Challenge, Submission, Team, get_scoreboard
from django.conf import settings
from web.forms import TeamCreateForm, UserCreationForm, UserChangeForm, AdminPageForm
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
    user = request.user
    name = path.split("/")[-1] if path else "index"
    page = get_object_or_404(Page, name=name)
    context = {}
    if user.is_superuser:
        if request.method == "POST":
            form = AdminPageForm(request.POST, instance=page)
            if form.is_valid():
                page = form.save()
        else:
            form = AdminPageForm(instance=page)
        template = "web/admin_page.html" 
        context["form"] = form
    else: 
        template = "web/page.html"
    
    context["body"] = page.content
    context["type"] = page.type
    return render(request, template, context)

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
    
    if request.method == "POST" and team_id:
        if "flag" in request.POST:
            flag = request.POST["flag"]
            if challenge.is_flag(flag):
                solved = Submission(team_id=team_id, challenge=challenge, solved_by=user)
                solved.save()
                challenge.is_solved = True

    return render(request, "web/challenge.html", {"challenge": challenge})


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
    team = get_object_or_404(Team, id=id)
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
