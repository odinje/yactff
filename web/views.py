from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, JsonResponse
from django.contrib.auth.decorators import user_passes_test
from web.utils import load_page, get_or_none, allow_view
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from web.models import Page, Category, Challenge, Team, SolvedChallenge
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


@login_required
def challenges(request):
    categories = Category.objects.all()
    
    team = get_or_none(Team, player=request.user.id)
    challenges = Challenge.objects.with_solves(team=team.id)
    return render(request, "web/challenges.html", {"challenges": challenges,
                                                   "categories": categories})


@login_required
def challenge(request, id):
    team = get_or_none(Team, player=request.user.id)
    challenge = Challenge.objects.with_solves(team=team.id, challenge=id)
    
    if request.method == "POST":
        if "flag" in request.POST:
            flag = request.POST["flag"]
            if challenge.is_flag(flag):
                solved = SolvedChallenge(team=team, challenge=challenge)
                solved.save()
                challenge.is_solved = True

    return render(request, "web/challenge.html", {"challenge": challenge})


@login_required
def user_profile(request):
    return render(request, "web/profile.html")

@user_passes_test(lambda u: u.is_superuser) #TODO: Maybe change to is_staff?
def download_page_file(request, id, filename):
    filepath = settings.PAGE_DIR + filename 
    response = HttpResponse(load_page(filepath), "applicaion/text")
    response['Content-Disposition'] = "attachment; filename={0}".format(filename)
    response['Content-Length'] = os.path.getsize(filepath)
    return response
