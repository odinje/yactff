from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from web.models import Submission, Team
from django.conf import settings
from web.forms import TeamCreateForm
from web.decorator import team_required, not_in_team


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
            messages.info(request, "Joined, {}".format(team.name))
            return redirect("team_profile")
        except:
            messages.error(request, "Team not found")
            return redirect("user_profile")
    else:
        return HttpResponse(status=405)
