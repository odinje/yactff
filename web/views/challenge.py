
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.cache import cache
import sys
import hashlib
from web.models import (
        Category,
        Challenge,
        Submission,
        get_scoreboard,
        )
from django.conf import settings
from web.forms import (
        AdminChallengeForm,
        AdminCategoryForm,
        )
from web.decorator import (
        admin_required,
        game_active,
        )
from web.utils import (
        random_string,
        create_zip,
        pause_game as _pause_game,
        )


@login_required
@game_active
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
@game_active
def challenge(request, id):
    user = request.user
    team_id = user.team_id
    challenge = Challenge.objects.with_solves(team=team_id, challenge=id)
    context = {}
    if user.is_superuser:
        template = "web/admin_challenge.html"
        if request.method == "POST":
            form = AdminChallengeForm(request.POST,  instance=challenge)
            files = request.FILES.getlist("files")
            if form.is_valid():
                new_challenge = form.save(commit=False)
                if files:
                    files_zip = create_zip(files)
                    files_zip.seek(0)
                    new_challenge.file = InMemoryUploadedFile(files_zip, None, "{}.zip".format(hashlib.sha256(files_zip.read()).hexdigest()), "application/zip", sys.getsizeof(files_zip), charset=None)
                new_challenge.save()
        else:
            form = AdminChallengeForm(instance=challenge)
        context["form"] = form
        context["submissions"] = Submission.objects.filter(challenge_id=challenge.id)
    else:
        template = "web/challenge.html"
        if not challenge.active:  # TODO: Rename active => is_active
            raise Http404
    context["challenge"] = challenge
    context["flag_format"] = settings.CTF_FLAG_FORMAT
    context["solves_procent"] = challenge.solves() * 100
    if request.method == "POST" and team_id and not challenge.is_solved:
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
        challenge = Challenge.objects.create(title=challenge_name, category=first_category, author=request.user, key=settings.CTF_FLAG_FORMAT)
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


def scoreboard_json(request):
    scores = cache.get_or_set("scoreboard", get_scoreboard())
    return JsonResponse(scores, safe=False)


@admin_required
def pause_game(request):
    _pause_game()
    return redirect("index")


