from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, JsonResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from web.models import (
        Page,
        Category,
        Challenge,
        Submission,
        Team,
        get_scoreboard,
        User
        )
from django.conf import settings
from web.forms import (
        TeamCreateForm,
        UserCreationForm,
        UserChangeForm,
        AdminPageForm,
        AdminChallengeForm,
        AdminCategoryForm,
        AdminUserChangeForm
        )
from web.decorator import (
        team_required,
        not_in_team,
        anonymous_required,
        admin_required
        )
from web.utils import random_string
from web.utils import delete_page_file


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
            old_name = page.name
            old_type = page.type
            form = AdminPageForm(request.POST, instance=page)
            if form.is_valid():
                page = form.save()
                if old_name != page.name:
                    delete_page_file(old_name, old_type)
                    return redirect("page", path=page.name)
        else:
            form = AdminPageForm(instance=page)
        pages = Page.objects.all()
        template = "web/admin_page.html"
        context["form"] = form
        context["pages"] = pages
    else:
        template = "web/page.html"

    context["page"] = page
    return render(request, template, context)


@admin_required
def page_add(request):
    page_name = random_string()
    try:
        Page.objects.create(name=page_name, content="Text Here")
        return redirect("page", path=page_name)
    except:
        raise Http404  # Change to more useful return code


@admin_required
def page_remove(request, id):
    page = get_object_or_404(Page, id=id)
    if page.name != "index":  # Cannot delete index, maybe give value error?
        page.delete()
    return redirect("index")


@login_required
def challenges(request):
    user = request.user
    categories = Category.objects.all()
    challenges = Challenge.objects.with_solves(team=user.team_id)
    context = {}
    if user.is_superuser:
        template = "web/admin_challenges.html"
        if request.method == "POST":
            form = [AdminCategoryForm(request.POST, instance=category, prefix=category.name) for category in categories]
            form.append(AdminCategoryForm(request.POST, prefix="new_category"))
            for pos, f in enumerate(form):
                if f.is_valid():
                    print(pos)
                    if pos == len(form)-1 and f.cleaned_data["name"] == "":
                        break
                    elif f.cleaned_data["delete"]:
                        f.instance.delete()
                    else:
                        f.save()
            return redirect("challenges")
        else:
            form = [AdminCategoryForm(instance=category, prefix=category.name) for category in categories]
            form.append(AdminCategoryForm(prefix="new_category"))
        context["form"] = form
    else:
        template = "web/challenges.html"
    context["challenges"] = challenges
    context["categories"] = categories

    return render(request, template, context)


@login_required
def challenge(request, id):
    user = request.user
    team_id = user.team_id
    challenge = Challenge.objects.with_solves(team=team_id, challenge=id)
    context = {}
    if user.is_superuser:
        template = "web/admin_challenge.html"
        if request.method == "POST":
            form = AdminChallengeForm(request.POST, instance=challenge)
            if form.is_valid():
                form.save()
        else:
            form = AdminChallengeForm(instance=challenge)
        context["form"] = form
        context["submissions"] = Submission.objects.filter(challenge_id=challenge.id)
    else:
        template = "web/challenge.html"
        if not challenge.active:  # TODO: Rename active => is_active
            raise Http404
    context["challenge"] = challenge
    if request.method == "POST" and team_id:
        if "flag" in request.POST:
            flag = request.POST["flag"]
            if challenge.is_flag(flag):
                solved = Submission(team_id=team_id, challenge=challenge, solved_by=user)
                solved.save()
                challenge.is_solved = True

    return render(request, template, context)


@admin_required
def challenge_add(request):
    challenge_name = random_string()
    try:
        first_category = Category.objects.filter()[:1].get()
        challenge = Challenge.objects.create(title=challenge_name, category=first_category, author=request.user)
        return redirect("challenge", id=challenge.id)
    except:
        raise Http404  # Change to more useful return code


@admin_required
def submission_remove(request, id):
    submission = get_object_or_404(Submission, id=id)
    challenge_id = submission.challenge_id
    submission.delete()
    return redirect("challenge", id=challenge_id)


def scoreboard(request):
    return render(request, "web/scoreboard.html")


def scoreboard_json(request):  # TODO: change to scoreboard_json
    scores = get_scoreboard()
    return JsonResponse(scores, safe=False)


@login_required
def user_profile(request):
    user = request.user
    team = user.team
    challenges = Submission.objects.get_solved(team=team, user=user)
    if request.method == "POST":
        userdata_form = UserChangeForm(request.POST, instance=user)
        password_form = PasswordChangeForm(user, request.POST)
        if userdata_form.is_valid():
            userdata_form.save()
        if password_form.is_valid():
            password_form.save()
    else:
        userdata_form = UserChangeForm(instance=user)
        password_form = PasswordChangeForm(user)
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


@admin_required
def user_all(request):
    users = User.objects.all()

    return render(request, "web/admin_users.html", {"users": users})


@admin_required
def user_show(request, id):
    user = User.objects.get(id=id)
    if request.method == "POST":
        form = AdminUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
    else:
        form = AdminUserChangeForm(instance=user)

    return render(request, "web/admin_user.html", {"target_user": user, "form": form})
