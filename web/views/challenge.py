from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.cache import cache
from django.views import View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.utils.decorators import method_decorator
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


game_decorators = [login_required, game_active]


@method_decorator(game_decorators, name="dispatch")
class ChallengesView(View):
    template_name = "web/challenges.html"

    def get(self, request, *args, **kwargs):
        user = request.user
        categories = Category.objects.all()
        challenges = Challenge.objects.with_solves(team=user.team_id)

        context = {}
        context["challenges"] = challenges
        context["categories"] = categories

        return render(request, self.template_name, context)


@method_decorator(game_decorators, name="dispatch")
class ChallengeView(View):
    template_name = "web/challenge.html"

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        self.team_id = self.user.team_id
        self.challenge_id = kwargs["id"]
        if not Challenge.objects.filter(pk=self.challenge_id).exists():
            raise Http404
        self.challenge = Challenge.objects.with_solves(team=self.team_id, challenge=self.challenge_id)

        if not self.challenge.active:
            raise Http404

        return super(ChallengeView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = {}
        context["challenge"] = self.challenge
        context["flag_format"] = settings.CTF_FLAG_FORMAT
        context["solves_procent"] = self.challenge.solves() * 100

        return render(self.request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if self.team_id and not self.challenge.is_solved:
            if "flag" in request.POST:
                flag = request.POST["flag"]
                if self.challenge.is_flag(flag):
                    solved = Submission(team_id=self.team_id, challenge=self.challenge, solved_by=self.user)
                    solved.save()
                    self.challenge.is_solved = True
        else:
            raise Http404
        return redirect("challenge", id=self.challenge_id)


@method_decorator([admin_required], name="dispatch")
class AdminCompetitionView(ChallengesView):
    template_name = "web/admin_competition_list.html"


@method_decorator([admin_required], name="dispatch")
class AdminCategoryCreate(CreateView):
    model = Category
    fields = ["name"]
    template_name = "web/default_form.html"
    success_url = reverse_lazy("admin-competition")


@method_decorator([admin_required], name="dispatch")
class AdminChallengeCreate(CreateView):
    model = Challenge
    fields = "__all__"
    template_name = "web/default_form.html"
    success_url = reverse_lazy("admin-competition")


@method_decorator([admin_required], name="dispatch")
class AdminChallengeUpdate(UpdateView):
    model = Challenge
    fields = "__all__"
    template_name = "web/default_form.html"
    success_url = reverse_lazy("admin-competition")


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
